from __future__ import annotations

import argparse

from navbot_x_isaac_lab.demo.inspection_mission import InspectionMission
from navbot_x_isaac_lab.demo.layout_blueprint import AegisLayoutBlueprint


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="NavBot-X Isaac Lab app entry for Aegis Inspection Bay."
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run without rendering window.",
    )
    parser.add_argument(
        "--preview-only",
        action="store_true",
        help="Only print blueprint and mission summary, do not launch simulator.",
    )
    parser.add_argument(
        "--max-steps",
        type=int,
        default=3200,
        help="How many simulation steps to keep the scene alive.",
    )
    parser.add_argument(
        "--play-demo-route",
        action="store_true",
        help="Play the scripted Inspection Route Alpha rover motion.",
    )
    parser.add_argument(
        "--cinematic-demo",
        action="store_true",
        help="Enable automatic camera sequence during the demo.",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    blueprint = AegisLayoutBlueprint()
    mission = InspectionMission()

    print("=== NAVBOT-X ISAAC LAB APP ENTRY ===")
    print(f"Headless Mode : {args.headless}")
    print(f"Preview Only  : {args.preview_only}")
    print(f"Play Demo     : {args.play_demo_route}")
    print(f"Cinematic     : {args.cinematic_demo}")
    print()

    print(blueprint.describe())
    print()
    mission.describe()
    print()

    if args.preview_only:
        print("Preview complete. No simulator launched.")
        return

    from isaacsim import SimulationApp

    simulation_app = SimulationApp({"headless": args.headless})

    from navbot_x_isaac_lab.demo.aegis_scene_builder import AegisSceneBuilder
    from navbot_x_isaac_lab.demo.route_animator import RouteAnimator

    builder = AegisSceneBuilder(blueprint=blueprint)
    builder.build()

    hero_camera = "/World/AegisInspectionBay/Cameras/HeroCamera"
    route_camera = "/World/AegisInspectionBay/Cameras/RouteCamera"
    top_camera = "/World/AegisInspectionBay/Cameras/TopCamera"

    if not args.headless:
        builder.set_active_camera(hero_camera)

    print("[APP STATUS] Aegis Inspection Bay scene created.")
    print("[STATUS] NavBot-X Rover spawned.")
    print("[STATUS] Omni-wheel flagship configuration active.")

    route_iterator = None
    if args.play_demo_route:
        route_animator = RouteAnimator("/World/AegisInspectionBay/NavBotXRover")
        route_iterator = route_animator.inspection_route_alpha()
        print("[DEMO] Scripted Inspection Route Alpha enabled.")

    step_count = 0
    switched_to_route = False
    switched_to_top = False

    while simulation_app.is_running() and step_count < args.max_steps:
        if route_iterator is not None:
            try:
                next(route_iterator)
            except StopIteration:
                route_iterator = None

        if args.cinematic_demo and not args.headless:
            # Start on hero cam with a slow pullback
            if step_count <= 110:
                builder.set_active_camera(hero_camera)
                builder.animate_hero_camera_pullback(
                    step_count=step_count,
                    start_step=0,
                    end_step=110,
                    start_pos=(-9.2, -5.2, 3.2),
                    end_pos=(-12.2, -7.4, 5.0),
                    camera_prim_path=hero_camera,
                )

            elif step_count > 110 and not switched_to_route:
                builder.set_active_camera(route_camera)
                switched_to_route = True

            elif step_count > 520 and not switched_to_top:
                builder.set_active_camera(top_camera)
                switched_to_top = True
        

        simulation_app.update()
        step_count += 1

    simulation_app.close()


if __name__ == "__main__":
    main()