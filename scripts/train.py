from navbot_x_isaac_lab.tasks.navigation import NavigationEnv, NavigationEnvCfg


def main():
    cfg = NavigationEnvCfg()
    env = NavigationEnv(cfg)

    print("NavBot-X Isaac Lab training placeholder")
    print(f"Task name      : {cfg.task_name}")
    print(f"Num envs       : {cfg.num_envs}")
    print(f"Episode length : {cfg.episode_length}")
    print(f"Sim dt         : {cfg.sim_dt}")

    env.reset()
    print("Training entry script placeholder is ready for future Isaac Lab integration.")


if __name__ == "__main__":
    main()