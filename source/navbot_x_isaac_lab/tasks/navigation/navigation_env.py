from .navigation_env_cfg import NavigationEnvCfg


class NavigationEnv:
    """Minimal placeholder navigation environment."""

    def __init__(self, cfg: NavigationEnvCfg | None = None):
        self.cfg = cfg if cfg is not None else NavigationEnvCfg()

    def reset(self):
        print(f"Resetting environment: {self.cfg.task_name}")
        return {"status": "reset"}

    def step(self, action):
        print(f"Stepping with action: {action}")
        obs = {"status": "running"}
        reward = 0.0
        terminated = False
        truncated = False
        info = {}
        return obs, reward, terminated, truncated, info