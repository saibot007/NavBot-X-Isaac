class NavigationEnvCfg:
    """Basic placeholder config for the first navigation task."""

    def __init__(self):
        self.task_name = "navigation"
        self.num_envs = 1
        self.episode_length = 500
        self.sim_dt = 0.02