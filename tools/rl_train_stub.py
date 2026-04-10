from __future__ import annotations

import numpy as np

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": False})

from navbot_x_isaac_lab.demo.aegis_scene_builder import AegisSceneBuilder
from navbot_x_isaac_lab.demo.layout_blueprint import AegisLayoutBlueprint
from navbot_x_isaac_lab.tasks.navigation.inspection_rl_env import InspectionRLEnv
from navbot_x_isaac_lab.tasks.navigation.inspection_rl_env_cfg import InspectionRLEnvCfg


class HeuristicPolicy:
    def act(self, obs):
        x, y, tx, ty, dx, dy, dist, yaw_norm = obs
        yaw_deg = yaw_norm * 180.0

        import math

        target_heading = math.degrees(math.atan2(dy, dx))
        heading_error = target_heading - yaw_deg

        while heading_error > 180.0:
            heading_error -= 360.0
        while heading_error < -180.0:
            heading_error += 360.0

        yaw_cmd = max(-1.0, min(1.0, heading_error / 45.0))

        if abs(heading_error) < 25.0:
            forward_cmd = 1.0
        else:
            forward_cmd = 0.2

        return np.array([forward_cmd, yaw_cmd], dtype=np.float32)


def main():
    blueprint = AegisLayoutBlueprint()
    builder = AegisSceneBuilder(blueprint=blueprint)
    builder.build()
    builder.set_active_camera("/World/AegisInspectionBay/Cameras/RouteCamera")

    cfg = InspectionRLEnvCfg()
    env = InspectionRLEnv(cfg=cfg)
    policy = HeuristicPolicy()

    num_episodes = 5
    rollout_horizon = 300

    for ep in range(num_episodes):
        obs = env.reset()
        episode_reward = 0.0

        rollout = {
            "obs": [],
            "actions": [],
            "rewards": [],
            "next_obs": [],
            "terminated": [],
            "truncated": [],
        }

        for step in range(rollout_horizon):
            action = policy.act(obs)
            next_obs, reward, terminated, truncated, info = env.step(action)

            rollout["obs"].append(obs.copy())
            rollout["actions"].append(action.copy())
            rollout["rewards"].append(float(reward))
            rollout["next_obs"].append(next_obs.copy())
            rollout["terminated"].append(bool(terminated))
            rollout["truncated"].append(bool(truncated))

            simulation_app.update()

            episode_reward += reward
            obs = next_obs

            if terminated or truncated:
                break

        print(
            f"episode={ep} steps={len(rollout['rewards'])} "
            f"episode_reward={episode_reward:.3f}"
        )

    simulation_app.close()


if __name__ == "__main__":
    main()