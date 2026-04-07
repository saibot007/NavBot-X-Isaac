from navbot_x_isaac_lab.demo.scene_config import AegisInspectionBayConfig


class InspectionMission:
    """Phase-1 mission definition for the flagship NavBot-X Isaac Lab demo."""

    def __init__(self, scene_cfg: AegisInspectionBayConfig | None = None):
        self.scene_cfg = scene_cfg if scene_cfg is not None else AegisInspectionBayConfig()

        self.project_name = "NavBot-X Isaac Lab"
        self.scene_name = self.scene_cfg.scene_name
        self.vehicle_name = self.scene_cfg.vehicle_name
        self.mission_name = self.scene_cfg.mission_name

        self.start_zone = "Deployment Zone"
        self.checkpoints = [checkpoint.name for checkpoint in self.scene_cfg.checkpoints]

    def describe(self):
        print(f"Project : {self.project_name}")
        print(f"Scene   : {self.scene_name}")
        print(f"Vehicle : {self.vehicle_name}")
        print(f"Mission : {self.mission_name}")
        print(f"Start   : {self.start_zone}")
        print("Route   : " + " -> ".join(self.checkpoints))
        print()
        print(self.scene_cfg.summary())

    def run_demo(self):
        print(f"[MISSION START] {self.mission_name}")
        print(f"{self.vehicle_name} deployed from {self.start_zone}")

        for checkpoint in self.checkpoints:
            print(f"{self.vehicle_name} visiting {checkpoint}")

        print(f"[MISSION COMPLETE] {self.vehicle_name} completed {self.mission_name}")


def main():
    mission = InspectionMission()
    mission.describe()
    print()
    mission.run_demo()


if __name__ == "__main__":
    main()