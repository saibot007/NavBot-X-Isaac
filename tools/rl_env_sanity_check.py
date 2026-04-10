from __future__ import annotations

import numpy as np

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": False})

from navbot_x_isaac_lab.demo.aegis_scene_builder import AegisSceneBuilder
from navbot_x_isaac_lab.demo.layout_blueprint import AegisLayoutBlueprint
from navbot_x_isaac_lab.tasks.navigation.inspection_rl_env import InspectionRLEnv
from navbot_x_isaac_lab.tasks.navigation.inspection_rl_env_cfg import InspectionRLEnvCfg


def main():
    blueprint = AegisLayoutBlueprint()
    builder = AegisSceneBuilder(blueprint=blueprint)
    builder.build()
    builder.set_active_camera("/World/AegisInspectionBay/Cameras/RouteCamera")

    cfg = InspectionRLEnvCfg()
    env = InspectionRLEnv(cfg=cfg)

    obs = env.reset()
    print("reset obs:", obs)

    step_count = 0
    while simulation_app.is_running() and step_count < 300:
        action = np.random.uniform(low=-1.0, high=1.0, size=(2,))
        obs, reward, terminated, truncated, info = env.step(action)

        print(
            f"step={step_count} reward={reward:.3f} "
            f"terminated={terminated} truncated={truncated} "
            f"dist={info['distance_to_target']:.3f}"
        )

        simulation_app.update()
        step_count += 1

        if terminated or truncated:
            print("episode ended, resetting")
            obs = env.reset()

    simulation_app.close()


if __name__ == "__main__":
    main()