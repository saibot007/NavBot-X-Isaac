from dataclasses import dataclass, field


@dataclass
class Vec3:
    x: float
    y: float
    z: float

    def as_tuple(self):
        return (self.x, self.y, self.z)


@dataclass
class Checkpoint:
    name: str
    position: Vec3
    description: str


@dataclass
class CameraPose:
    name: str
    position: Vec3
    look_at: Vec3
    description: str


@dataclass
class SceneObject:
    name: str
    kind: str
    position: Vec3
    scale: Vec3
    description: str


@dataclass
class AegisInspectionBayConfig:
    scene_name: str = "Aegis Inspection Bay"
    vehicle_name: str = "NavBot-X Rover"
    mission_name: str = "Inspection Route Alpha"

    # core footprint
    floor_size: Vec3 = field(default_factory=lambda: Vec3(24.0, 14.0, 0.2))
    lane_size: Vec3 = field(default_factory=lambda: Vec3(18.0, 3.4, 0.02))
    presentation_slab_size: Vec3 = field(default_factory=lambda: Vec3(20.0, 6.4, 0.02))

    # mission anchors
    deployment_zone: Vec3 = field(default_factory=lambda: Vec3(-8.0, 0.0, 0.0))
    hero_end_pose: Vec3 = field(default_factory=lambda: Vec3(8.2, 0.0, 0.0))

    # visual framing
    rear_wall_position: Vec3 = field(default_factory=lambda: Vec3(9.7, 0.0, 1.8))
    rear_wall_scale: Vec3 = field(default_factory=lambda: Vec3(0.35, 13.2, 3.6))

    left_wall_position: Vec3 = field(default_factory=lambda: Vec3(0.0, 6.85, 1.45))
    left_wall_scale: Vec3 = field(default_factory=lambda: Vec3(18.5, 0.22, 2.9))

    right_wall_position: Vec3 = field(default_factory=lambda: Vec3(0.0, -6.85, 1.45))
    right_wall_scale: Vec3 = field(default_factory=lambda: Vec3(18.5, 0.22, 2.9))

    # checkpoints
    checkpoints: list[Checkpoint] = field(
        default_factory=lambda: [
            Checkpoint(
                name="Checkpoint A",
                position=Vec3(-3.4, 2.2, 0.0),
                description="Premium scan node near the left inspection sector.",
            ),
            Checkpoint(
                name="Checkpoint B",
                position=Vec3(1.5, -2.0, 0.0),
                description="Central route diagnostic node.",
            ),
            Checkpoint(
                name="Checkpoint C",
                position=Vec3(6.4, 1.8, 0.0),
                description="Final validation node before hero finish.",
            ),
        ]
    )

    # authored cameras
    cameras: list[CameraPose] = field(
        default_factory=lambda: [
            CameraPose(
                name="HeroCamera",
                position=Vec3(-11.2, -6.8, 4.4),
                look_at=Vec3(-7.7, 0.0, 0.35),
                description="Premium front three-quarter hero camera.",
            ),
            CameraPose(
                name="RouteCamera",
                position=Vec3(-1.5, -13.5, 8.2),
                look_at=Vec3(2.0, 0.0, 0.25),
                description="Elevated cinematic route camera.",
            ),
            CameraPose(
                name="TopCamera",
                position=Vec3(0.0, 0.0, 20.0),
                look_at=Vec3(0.0, 0.0, 0.0),
                description="Top-down documentation camera.",
            ),
        ]
    )

    # authored scene masses
    scene_objects: list[SceneObject] = field(
        default_factory=lambda: [
            SceneObject(
                name="Left Machinery Core",
                kind="machinery_core",
                position=Vec3(-3.1, 4.85, 1.0),
                scale=Vec3(3.8, 1.15, 2.0),
                description="Large premium machinery mass for left-side framing.",
            ),
            SceneObject(
                name="Right Machinery Core",
                kind="machinery_core",
                position=Vec3(5.7, -4.75, 1.05),
                scale=Vec3(4.1, 1.25, 2.1),
                description="Primary right-side equipment mass.",
            ),
            SceneObject(
                name="Rear Service Tower",
                kind="service_tower",
                position=Vec3(7.85, 4.35, 1.55),
                scale=Vec3(1.7, 1.3, 3.1),
                description="Rear vertical form for depth and silhouette.",
            ),
            SceneObject(
                name="Front Pillar Left",
                kind="pillar",
                position=Vec3(-0.75, 5.45, 1.65),
                scale=Vec3(0.42, 0.42, 3.3),
                description="Left foreground pillar for scene framing.",
            ),
            SceneObject(
                name="Front Pillar Right",
                kind="pillar",
                position=Vec3(3.85, -5.45, 1.65),
                scale=Vec3(0.42, 0.42, 3.3),
                description="Right foreground pillar for scene framing.",
            ),
        ]
    )

    # visual identity notes
    lane_marking_style: str = "embedded premium route guidance with blue pulse logic"
    accent_lighting: str = "matte black bay with restrained gold and electric blue lighting"
    rover_palette: str = "matte black, graphite black, muted premium gold, electric blue"
    environment_palette: str = "deep graphite black, cool steel blacks, electric blue, cyan glow, restrained gold"

    def summary(self) -> str:
        lines = [
            f"Scene: {self.scene_name}",
            f"Vehicle: {self.vehicle_name}",
            f"Mission: {self.mission_name}",
            "",
            "--- Core Footprint ---",
            f"Floor Size: {self.floor_size.as_tuple()}",
            f"Lane Size: {self.lane_size.as_tuple()}",
            f"Presentation Slab: {self.presentation_slab_size.as_tuple()}",
            "",
            "--- Mission Anchors ---",
            f"Deployment Zone: {self.deployment_zone.as_tuple()}",
            f"Hero End Pose: {self.hero_end_pose.as_tuple()}",
            "",
            "--- Structural Framing ---",
            f"Rear Wall: pos={self.rear_wall_position.as_tuple()} scale={self.rear_wall_scale.as_tuple()}",
            f"Left Wall: pos={self.left_wall_position.as_tuple()} scale={self.left_wall_scale.as_tuple()}",
            f"Right Wall: pos={self.right_wall_position.as_tuple()} scale={self.right_wall_scale.as_tuple()}",
            "",
            "--- Checkpoints ---",
        ]

        for checkpoint in self.checkpoints:
            lines.append(
                f"  - {checkpoint.name}: {checkpoint.position.as_tuple()} | {checkpoint.description}"
            )

        lines.append("")
        lines.append("--- Cameras ---")
        for camera in self.cameras:
            lines.append(
                f"  - {camera.name}: pos={camera.position.as_tuple()} look_at={camera.look_at.as_tuple()}"
            )

        lines.append("")
        lines.append("--- Scene Objects ---")
        for obj in self.scene_objects:
            lines.append(
                f"  - {obj.name} [{obj.kind}]: pos={obj.position.as_tuple()} scale={obj.scale.as_tuple()}"
            )

        lines.append("")
        lines.append("--- Identity ---")
        lines.append(f"Lane Style: {self.lane_marking_style}")
        lines.append(f"Accent Lighting: {self.accent_lighting}")
        lines.append(f"Rover Palette: {self.rover_palette}")
        lines.append(f"Environment Palette: {self.environment_palette}")

        return "\n".join(lines)