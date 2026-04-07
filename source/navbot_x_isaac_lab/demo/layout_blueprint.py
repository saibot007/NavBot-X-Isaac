from dataclasses import dataclass, field

from navbot_x_isaac_lab.demo.scene_config import AegisInspectionBayConfig


@dataclass
class MaterialStyle:
    floor: str = "dark_graphite_metal"
    walls: str = "matte_steel"
    lane_markings: str = "white_yellow_guidance"
    checkpoint_glow: str = "cyan_emissive"
    accent_light: str = "cool_cyan_strip"


@dataclass
class LightingStyle:
    ambient: str = "cool_industrial"
    hero_intensity: float = 1.2
    fill_intensity: float = 0.6
    rim_intensity: float = 0.8


@dataclass
class RoverStyle:
    body_color: str = "dark_grey"
    accent_color: str = "electric_blue"
    trim_color: str = "silver"
    sensor_style: str = "front_sensor_pod"
    identity_note: str = "compact premium inspection rover"


@dataclass
class AegisLayoutBlueprint:
    scene_cfg: AegisInspectionBayConfig = field(default_factory=AegisInspectionBayConfig)
    materials: MaterialStyle = field(default_factory=MaterialStyle)
    lighting: LightingStyle = field(default_factory=LightingStyle)
    rover_style: RoverStyle = field(default_factory=RoverStyle)

    def describe(self) -> str:
        lines = [
            "=== AEGIS INSPECTION BAY LAYOUT BLUEPRINT ===",
            f"Scene Name      : {self.scene_cfg.scene_name}",
            f"Vehicle Name    : {self.scene_cfg.vehicle_name}",
            f"Mission Name    : {self.scene_cfg.mission_name}",
            "",
            "--- Material Style ---",
            f"Floor           : {self.materials.floor}",
            f"Walls           : {self.materials.walls}",
            f"Lane Markings   : {self.materials.lane_markings}",
            f"Checkpoint Glow : {self.materials.checkpoint_glow}",
            f"Accent Light    : {self.materials.accent_light}",
            "",
            "--- Lighting Style ---",
            f"Ambient         : {self.lighting.ambient}",
            f"Hero Intensity  : {self.lighting.hero_intensity}",
            f"Fill Intensity  : {self.lighting.fill_intensity}",
            f"Rim Intensity   : {self.lighting.rim_intensity}",
            "",
            "--- Rover Style ---",
            f"Body Color      : {self.rover_style.body_color}",
            f"Accent Color    : {self.rover_style.accent_color}",
            f"Trim Color      : {self.rover_style.trim_color}",
            f"Sensor Style    : {self.rover_style.sensor_style}",
            f"Identity        : {self.rover_style.identity_note}",
            "",
            "--- Route Summary ---",
            f"Deployment Zone : {self.scene_cfg.deployment_zone.as_tuple()}",
            f"Hero End Pose   : {self.scene_cfg.hero_end_pose.as_tuple()}",
        ]

        for cp in self.scene_cfg.checkpoints:
            lines.append(f"{cp.name:15}: {cp.position.as_tuple()}")

        return "\n".join(lines)


def main():
    blueprint = AegisLayoutBlueprint()
    print(blueprint.describe())


if __name__ == "__main__":
    main()