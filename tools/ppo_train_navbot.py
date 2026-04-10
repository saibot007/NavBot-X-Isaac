from __future__ import annotations

import argparse
import os
from dataclasses import dataclass

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim


def build_parser():
    parser = argparse.ArgumentParser(description="Train NavBot-X PPO navigation policy.")
    parser.add_argument("--headless", action="store_true", help="Run Isaac Sim headless.")
    parser.add_argument("--total-timesteps", type=int, default=20000)
    parser.add_argument("--rollout-steps", type=int, default=512)
    parser.add_argument("--ppo-epochs", type=int, default=8)
    parser.add_argument("--minibatch-size", type=int, default=128)
    parser.add_argument("--save-every", type=int, default=5, help="Save every N updates.")
    parser.add_argument(
        "--checkpoint-dir",
        type=str,
        default="/home/atharva-sharma/NewStorage/projects/navbot-x-isaac-lab/checkpoints",
    )
    parser.add_argument(
        "--resume-checkpoint",
        type=str,
        default="",
        help="Path to a saved PPO checkpoint to resume or fine-tune from.",
    )
    parser.add_argument(
        "--load-optimizers",
        action="store_true",
        help="Also restore optimizer states when resuming.",
    )
    return parser


@dataclass
class PPOConfig:
    gamma: float = 0.99
    gae_lambda: float = 0.95
    clip_eps: float = 0.2
    policy_lr: float = 3e-4
    value_lr: float = 1e-3
    entropy_coef: float = 0.008
    value_coef: float = 0.5
    max_grad_norm: float = 0.5


class PolicyNet(nn.Module):
    def __init__(self, obs_dim: int = 8, act_dim: int = 2):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh(),
        )
        self.mean_head = nn.Linear(64, act_dim)
        self.log_std = nn.Parameter(torch.full((act_dim,), -0.85))

    def forward(self, obs: torch.Tensor):
        x = self.net(obs)
        mean = self.mean_head(x)
        log_std = torch.clamp(self.log_std, min=-2.5, max=0.5)
        std = torch.exp(log_std)
        return mean, std


class ValueNet(nn.Module):
    def __init__(self, obs_dim: int = 8):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(obs_dim, 64),
            nn.Tanh(),
            nn.Linear(64, 64),
            nn.Tanh(),
            nn.Linear(64, 1),
        )

    def forward(self, obs: torch.Tensor):
        return self.net(obs).squeeze(-1)


def sample_action(policy: PolicyNet, obs_np: np.ndarray):
    obs_t = torch.tensor(obs_np, dtype=torch.float32).unsqueeze(0)
    with torch.no_grad():
        mean, std = policy(obs_t)
        dist = torch.distributions.Normal(mean, std)
        raw_action = dist.sample()
        squashed_action = torch.tanh(raw_action)
        logp = dist.log_prob(raw_action).sum(dim=-1)
    return (
        squashed_action.squeeze(0).cpu().numpy().astype(np.float32),
        logp.item(),
    )


def evaluate_actions(policy: PolicyNet, obs_batch: torch.Tensor, act_batch: torch.Tensor):
    mean, std = policy(obs_batch)
    dist = torch.distributions.Normal(mean, std)

    act_batch = torch.clamp(act_batch, -0.999, 0.999)
    raw_action = 0.5 * torch.log((1.0 + act_batch) / (1.0 - act_batch))

    logp = dist.log_prob(raw_action).sum(dim=-1)
    entropy = dist.entropy().sum(dim=-1)
    return logp, entropy


def compute_gae(rewards, values, dones, last_value, gamma=0.99, gae_lambda=0.95):
    advantages = np.zeros_like(rewards, dtype=np.float32)
    gae = 0.0

    for t in reversed(range(len(rewards))):
        next_value = last_value if t == len(rewards) - 1 else values[t + 1]
        nonterminal = 1.0 - dones[t]
        delta = rewards[t] + gamma * next_value * nonterminal - values[t]
        gae = delta + gamma * gae_lambda * nonterminal * gae
        advantages[t] = gae

    returns = advantages + values
    return advantages, returns


def save_checkpoint(checkpoint_dir, update_idx, policy, value_fn, policy_optim, value_optim):
    os.makedirs(checkpoint_dir, exist_ok=True)
    path = os.path.join(checkpoint_dir, f"ppo_navbot_update_{update_idx:04d}.pt")
    torch.save(
        {
            "update": update_idx,
            "policy_state_dict": policy.state_dict(),
            "value_state_dict": value_fn.state_dict(),
            "policy_optim_state_dict": policy_optim.state_dict(),
            "value_optim_state_dict": value_optim.state_dict(),
        },
        path,
    )
    print(f"[CHECKPOINT] Saved: {path}")


def load_checkpoint(
    checkpoint_path: str,
    policy: PolicyNet,
    value_fn: ValueNet,
    policy_optim: optim.Optimizer | None = None,
    value_optim: optim.Optimizer | None = None,
    load_optimizers: bool = False,
):
    checkpoint = torch.load(checkpoint_path, map_location="cpu")

    policy.load_state_dict(checkpoint["policy_state_dict"])
    value_fn.load_state_dict(checkpoint["value_state_dict"])

    if load_optimizers:
        if policy_optim is not None and "policy_optim_state_dict" in checkpoint:
            policy_optim.load_state_dict(checkpoint["policy_optim_state_dict"])
        if value_optim is not None and "value_optim_state_dict" in checkpoint:
            value_optim.load_state_dict(checkpoint["value_optim_state_dict"])

    loaded_update = int(checkpoint.get("update", 0))
    print(f"[CHECKPOINT] Loaded: {checkpoint_path}")
    print(f"[CHECKPOINT] Starting from saved update index: {loaded_update}")
    print(f"[CHECKPOINT] Optimizers restored: {load_optimizers}")
    return loaded_update


def main():
    args = build_parser().parse_args()
    ppo_cfg = PPOConfig()

    from isaacsim import SimulationApp
    simulation_app = SimulationApp({"headless": args.headless})

    from navbot_x_isaac_lab.demo.aegis_scene_builder import AegisSceneBuilder
    from navbot_x_isaac_lab.demo.layout_blueprint import AegisLayoutBlueprint
    from navbot_x_isaac_lab.tasks.navigation.inspection_rl_env import InspectionRLEnv
    from navbot_x_isaac_lab.tasks.navigation.inspection_rl_env_cfg import InspectionRLEnvCfg

    blueprint = AegisLayoutBlueprint()
    builder = AegisSceneBuilder(blueprint=blueprint)
    builder.build()

    if not args.headless:
        builder.set_active_camera("/World/AegisInspectionBay/Cameras/RouteCamera")

    env = InspectionRLEnv(cfg=InspectionRLEnvCfg())

    obs_dim = 8
    act_dim = 2

    policy = PolicyNet(obs_dim, act_dim)
    value_fn = ValueNet(obs_dim)

    policy_optim = optim.Adam(policy.parameters(), lr=ppo_cfg.policy_lr)
    value_optim = optim.Adam(value_fn.parameters(), lr=ppo_cfg.value_lr)

    update_idx = 0
    if args.resume_checkpoint:
        if not os.path.exists(args.resume_checkpoint):
            raise FileNotFoundError(f"Checkpoint not found: {args.resume_checkpoint}")
        update_idx = load_checkpoint(
            checkpoint_path=args.resume_checkpoint,
            policy=policy,
            value_fn=value_fn,
            policy_optim=policy_optim,
            value_optim=value_optim,
            load_optimizers=args.load_optimizers,
        )

    obs = env.reset()
    total_steps = 0
    episode_reward = 0.0
    episode_len = 0
    episode_count = 0
    success_count = 0
    recent_final_dists = []

    while total_steps < args.total_timesteps:
        obs_buf = []
        act_buf = []
        logp_buf = []
        rew_buf = []
        done_buf = []
        val_buf = []

        for _ in range(args.rollout_steps):
            obs_t = torch.tensor(obs, dtype=torch.float32).unsqueeze(0)
            with torch.no_grad():
                value = value_fn(obs_t).item()

            action, logp = sample_action(policy, obs)
            next_obs, reward, terminated, truncated, info = env.step(action)

            done = float(terminated or truncated)

            obs_buf.append(obs.copy())
            act_buf.append(action.copy())
            logp_buf.append(logp)
            rew_buf.append(float(reward))
            done_buf.append(done)
            val_buf.append(value)

            simulation_app.update()

            episode_reward += reward
            episode_len += 1
            total_steps += 1
            obs = next_obs

            if terminated or truncated:
                episode_count += 1
                if info.get("success", False):
                    success_count += 1

                recent_final_dists.append(info["distance_to_target"])
                if len(recent_final_dists) > 20:
                    recent_final_dists.pop(0)

                print(
                    f"[ROLLOUT] episode={episode_count} "
                    f"len={episode_len} reward={episode_reward:.3f} "
                    f"final_dist={info['distance_to_target']:.3f} "
                    f"success={info.get('success', False)} "
                    f"stage={info.get('mission_stage', -1)} "
                    f"target={info.get('target_name', 'unknown')} "
                    f"reached_stage_target={info.get('reached_stage_target', False)} "
                    f"stage_bonus={info.get('stage_bonus', 0.0):.2f} "
                    f"target_index={info.get('target_index', -1)}"
                )
                obs = env.reset()
                episode_reward = 0.0
                episode_len = 0

            if total_steps >= args.total_timesteps:
                break

        obs_t = torch.tensor(obs, dtype=torch.float32).unsqueeze(0)
        with torch.no_grad():
            last_value = value_fn(obs_t).item()

        rewards = np.array(rew_buf, dtype=np.float32)
        values = np.array(val_buf, dtype=np.float32)
        dones = np.array(done_buf, dtype=np.float32)

        advantages, returns = compute_gae(
            rewards=rewards,
            values=values,
            dones=dones,
            last_value=last_value,
            gamma=ppo_cfg.gamma,
            gae_lambda=ppo_cfg.gae_lambda,
        )

        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)

        obs_batch = torch.tensor(np.array(obs_buf), dtype=torch.float32)
        act_batch = torch.tensor(np.array(act_buf), dtype=torch.float32)
        old_logp_batch = torch.tensor(np.array(logp_buf), dtype=torch.float32)
        adv_batch = torch.tensor(advantages, dtype=torch.float32)
        return_batch = torch.tensor(returns, dtype=torch.float32)

        batch_size = obs_batch.shape[0]
        indices = np.arange(batch_size)

        last_policy_loss = 0.0
        last_value_loss = 0.0
        last_entropy = 0.0

        for _epoch in range(args.ppo_epochs):
            np.random.shuffle(indices)

            for start in range(0, batch_size, args.minibatch_size):
                end = start + args.minibatch_size
                mb_idx = indices[start:end]

                mb_obs = obs_batch[mb_idx]
                mb_act = act_batch[mb_idx]
                mb_old_logp = old_logp_batch[mb_idx]
                mb_adv = adv_batch[mb_idx]
                mb_returns = return_batch[mb_idx]

                new_logp, entropy = evaluate_actions(policy, mb_obs, mb_act)
                ratio = torch.exp(new_logp - mb_old_logp)

                surr1 = ratio * mb_adv
                surr2 = torch.clamp(ratio, 1.0 - ppo_cfg.clip_eps, 1.0 + ppo_cfg.clip_eps) * mb_adv
                policy_loss = -torch.min(surr1, surr2).mean()

                value_pred = value_fn(mb_obs)
                value_loss = ((value_pred - mb_returns) ** 2).mean()

                entropy_bonus = entropy.mean()

                loss = (
                    policy_loss
                    + ppo_cfg.value_coef * value_loss
                    - ppo_cfg.entropy_coef * entropy_bonus
                )

                policy_optim.zero_grad()
                value_optim.zero_grad()
                loss.backward()

                nn.utils.clip_grad_norm_(policy.parameters(), ppo_cfg.max_grad_norm)
                nn.utils.clip_grad_norm_(value_fn.parameters(), ppo_cfg.max_grad_norm)

                policy_optim.step()
                value_optim.step()

                last_policy_loss = policy_loss.item()
                last_value_loss = value_loss.item()
                last_entropy = entropy_bonus.item()

        update_idx += 1
        avg_final_dist = (
            sum(recent_final_dists) / len(recent_final_dists)
            if recent_final_dists else float("nan")
        )

        print(
            f"[UPDATE] {update_idx} "
            f"steps={total_steps} "
            f"rollout={batch_size} "
            f"policy_loss={last_policy_loss:.4f} "
            f"value_loss={last_value_loss:.4f} "
            f"entropy={last_entropy:.4f} "
            f"successes={success_count} "
            f"avg_final_dist_20={avg_final_dist:.3f}"
        )

        if update_idx % args.save_every == 0:
            save_checkpoint(
                args.checkpoint_dir,
                update_idx,
                policy,
                value_fn,
                policy_optim,
                value_optim,
            )

    simulation_app.close()


if __name__ == "__main__":
    main()