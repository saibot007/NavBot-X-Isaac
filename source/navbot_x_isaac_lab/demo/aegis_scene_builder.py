from __future__ import annotations

from navbot_x_isaac_lab.demo.layout_blueprint import AegisLayoutBlueprint
from navbot_x_isaac_lab.demo.scene_config import AegisInspectionBayConfig


class AegisSceneBuilder:
    """Builds the first real Isaac-side version of Aegis Inspection Bay.

    Important:
    Omniverse / pxr imports are intentionally delayed until build-time,
    after SimulationApp has already been created.
    """

    def __init__(self, blueprint: AegisLayoutBlueprint | None = None):
        self.blueprint = blueprint if blueprint is not None else AegisLayoutBlueprint()
        self.scene_cfg: AegisInspectionBayConfig = self.blueprint.scene_cfg

        self.root_path = "/World/AegisInspectionBay"
        self.floor_path = f"{self.root_path}/Floor"
        self.lane_path = f"{self.root_path}/InspectionLane"
        self.props_path = f"{self.root_path}/Props"
        self.checkpoints_path = f"{self.root_path}/Checkpoints"
        self.rover_path = f"{self.root_path}/NavBotXRover"
        self.lights_path = f"{self.root_path}/Lights"
        self.cameras_path = f"{self.root_path}/Cameras"
        self.markers_path = f"{self.root_path}/Markers"

        self.stage = None
        self._UsdGeom = None
        self._UsdLux = None
        self._Gf = None

    def build(self):
        self._late_imports()

        self._ensure_xform(self.root_path)
        self._ensure_xform(self.props_path)
        self._ensure_xform(self.checkpoints_path)
        self._ensure_xform(self.lights_path)
        self._ensure_xform(self.cameras_path)
        self._ensure_xform(self.markers_path)

        self._build_floor()
        self._build_lane()
        self._build_deployment_zone()
        self._build_checkpoints()
        self._build_scene_objects()
        self._build_rover_placeholder()
        self._build_lights()
        self._build_cameras()

    def _late_imports(self):
        from pxr import Gf, UsdGeom, UsdLux
        import omni.usd

        self._Gf = Gf
        self._UsdGeom = UsdGeom
        self._UsdLux = UsdLux
        self.stage = omni.usd.get_context().get_stage()

        if self.stage is None:
            raise RuntimeError("USD stage is not available.")

    def _ensure_xform(self, prim_path: str):
        if self.stage.GetPrimAtPath(prim_path):
            return
        self._UsdGeom.Xform.Define(self.stage, prim_path)

    def _set_transform(self, prim, translation=None, scale=None):
        xform = self._UsdGeom.Xformable(prim)

        if translation is not None:
            translate_op = None
            for op in xform.GetOrderedXformOps():
                if op.GetOpType() == self._UsdGeom.XformOp.TypeTranslate:
                    translate_op = op
                    break
            if translate_op is None:
                translate_op = xform.AddTranslateOp()
            translate_op.Set(self._Gf.Vec3d(*translation))

        if scale is not None:
            scale_op = None
            for op in xform.GetOrderedXformOps():
                if op.GetOpType() == self._UsdGeom.XformOp.TypeScale:
                    scale_op = op
                    break
            if scale_op is None:
                scale_op = xform.AddScaleOp()
            scale_op.Set(self._Gf.Vec3f(*scale))

    def _create_cube(self, prim_path, translation, scale, color):
        cube = self._UsdGeom.Cube.Define(self.stage, prim_path)
        cube.CreateSizeAttr(1.0)
        self._set_transform(cube.GetPrim(), translation=translation, scale=scale)
        self._apply_display_color(cube.GetPrim(), color)
        return cube

    def _create_cylinder(self, prim_path, translation, radius, height, color, axis="Z"):
        cyl = self._UsdGeom.Cylinder.Define(self.stage, prim_path)
        cyl.CreateRadiusAttr(radius)
        cyl.CreateHeightAttr(height)
        cyl.CreateAxisAttr(axis)
        self._set_transform(cyl.GetPrim(), translation=translation)
        self._apply_display_color(cyl.GetPrim(), color)
        return cyl

    def _apply_display_color(self, prim, color):
        gprim = self._UsdGeom.Gprim(prim)
        gprim.CreateDisplayColorAttr([self._Gf.Vec3f(*color)])

    def _build_floor(self):
        floor_size = self.scene_cfg.floor_size.as_tuple()
        floor_z = floor_size[2] * 0.5

    # main floor
        self._create_cube(
            prim_path=self.floor_path,
            translation=(0.0, 0.0, floor_z),
            scale=floor_size,
            color=(0.045, 0.045, 0.05),
        )

    # central presentation slab
        self._create_cube(
            prim_path=f"{self.root_path}/PresentationSlab",
            translation=(0.5, 0.0, self.scene_cfg.floor_size.z + 0.01),
            scale=(20.0, 6.4, 0.02),
            color=(0.075, 0.08, 0.09),
        )

    # rear hero wall)
        self._create_cube(
            prim_path=f"{self.root_path}/RearHeroWall",
            translation=(9.7, 0.0, 1.8),
            scale=(0.35, 13.2, 3.6),
            color=(0.05, 0.05, 0.06),
        )

    # left frame wall
        self._create_cube(
            prim_path=f"{self.root_path}/LeftFrameWall",
            translation=(0.0, 6.85, 1.45),
            scale=(18.5, 0.22, 2.9),
            color=(0.055, 0.055, 0.065),
        )

    # right frame wall
        self._create_cube(
            prim_path=f"{self.root_path}/RightFrameWall",
            translation=(0.0, -6.85, 1.45),
            scale=(18.5, 0.22, 2.9),
            color=(0.055, 0.055, 0.065),
        )

    # top blue accents
        self._create_cube(
            prim_path=f"{self.root_path}/LeftFrameAccent",
            translation=(0.0, 6.68, 2.35),
            scale=(14.0, 0.025, 0.04),
            color=(0.00, 0.42, 0.95),
        )

        self._create_cube(
            prim_path=f"{self.root_path}/RightFrameAccent",
            translation=(0.0, -6.68, 2.35),
            scale=(14.0, 0.025, 0.04),
            color=(0.00, 0.42, 0.95),
        )

    # rear gold signature line
        self._create_cube(
            prim_path=f"{self.root_path}/RearGoldAccent",
            translation=(9.45, 0.0, 2.25),
            scale=(0.02, 7.5, 0.05),
            color=(0.72, 0.58, 0.22),
        )

    def _build_lane(self):
        lane_size = self.scene_cfg.lane_size.as_tuple()
        lane_z = self.scene_cfg.floor_size.z + lane_size[2] * 0.5

        self._create_cube(
            prim_path=self.lane_path,
            translation=(0.0, 0.0, lane_z),
            scale=lane_size,
            color=(0.10, 0.11, 0.13),
        )

        self._create_cube(
            prim_path=f"{self.markers_path}/LaneEdgeLeft",
            translation=(0.0, lane_size[1] * 0.5 - 0.08, lane_z + 0.01),
            scale=(lane_size[0], 0.05, 0.01),
            color=(0.00, 0.45, 1.00),
        )

        self._create_cube(
            prim_path=f"{self.markers_path}/LaneEdgeRight",
            translation=(0.0, -lane_size[1] * 0.5 + 0.08, lane_z + 0.01),
            scale=(lane_size[0], 0.05, 0.01),
            color=(0.00, 0.45, 1.00),
        )

        self._create_cube(
            prim_path=f"{self.markers_path}/LaneCenterPulse",
            translation=(0.0, 0.0, lane_z + 0.012),
            scale=(lane_size[0] * 0.85, 0.10, 0.01),
            color=(0.18, 0.85, 1.00),
        )

    # segmented guidance blocks for a more intentional route aesthetic
        segment_x = [-6.0, -2.0, 2.0, 6.0]
        for i, x in enumerate(segment_x):
            self._create_cube(
                prim_path=f"{self.markers_path}/RouteSegment_{i}",
                translation=(x, 0.0, lane_z + 0.015),
                scale=(1.1, 0.28, 0.01),
                color=(0.00, 0.38, 0.95),
            )

    def _build_deployment_zone(self):
        pos = self.scene_cfg.deployment_zone.as_tuple()
        z = self.scene_cfg.floor_size.z + 0.015

        self._create_cube(
            prim_path=f"{self.markers_path}/DeploymentPad",
            translation=(pos[0], pos[1], z),
            scale=(1.8, 1.8, 0.02),
            color=(0.10, 0.45, 0.80),
        )

        self._create_cube(
            prim_path=f"{self.markers_path}/HeroEndPad",
            translation=(self.scene_cfg.hero_end_pose.x, self.scene_cfg.hero_end_pose.y, z),
            scale=(1.5, 1.5, 0.02),
            color=(0.18, 0.80, 0.88),
        )

    def _build_checkpoints(self):
        floor_top = self.scene_cfg.floor_size.z

        for checkpoint in self.scene_cfg.checkpoints:
            cp = checkpoint.position.as_tuple()
            base_name = checkpoint.name.replace(" ", "")

            self._create_cylinder(
                prim_path=f"{self.checkpoints_path}/{base_name}Base",
                translation=(cp[0], cp[1], floor_top + 0.08),
                radius=0.50,
                height=0.14,
                color=(0.05, 0.06, 0.08),
            )

            self._create_cylinder(
                prim_path=f"{self.checkpoints_path}/{base_name}Glow",
                translation=(cp[0], cp[1], floor_top + 0.18),
                radius=0.28,
                height=0.08,
                color=(0.18, 0.85, 1.00),
            )

            self._create_cube(
                prim_path=f"{self.checkpoints_path}/{base_name}Beacon",
                translation=(cp[0], cp[1], floor_top + 0.82),
                scale=(0.10, 0.10, 1.0),
                color=(0.20, 0.90, 1.00),
            )

            self._create_cube(
                prim_path=f"{self.checkpoints_path}/{base_name}TopCap",
                translation=(cp[0], cp[1], floor_top + 1.30),
                scale=(0.20, 0.20, 0.06),
                color=(0.00, 0.45, 1.00),
            )

    def _build_scene_objects(self):
        matte_black = (0.055, 0.055, 0.065)
        graphite = (0.08, 0.085, 0.095)
        premium_gold = (0.72, 0.58, 0.22)
        electric_blue = (0.00, 0.42, 0.95)
        cyan_glow = (0.20, 0.85, 1.00)

        # left machinery bank
        self._create_cube(
            prim_path=f"{self.props_path}/LeftMachineryCore",
            translation=(-3.1, 4.85, 1.0),
            scale=(3.8, 1.15, 2.0),
            color=matte_black,
        )
        self._create_cube(
            prim_path=f"{self.props_path}/LeftMachineryUpper",
            translation=(-3.25, 4.85, 1.95),
            scale=(2.2, 0.7, 0.22),
            color=graphite,
        )
        self._create_cube(
            prim_path=f"{self.props_path}/LeftMachineryBlue",
            translation=(-3.1, 4.23, 1.55),
            scale=(2.5, 0.04, 0.04),
            color=electric_blue,
        )
        self._create_cube(
            prim_path=f"{self.props_path}/LeftMachineryGold",
            translation=(-3.1, 5.38, 1.18),
            scale=(1.5, 0.025, 0.03),
            color=premium_gold,
        )

    # right machinery bank
        self._create_cube(
            prim_path=f"{self.props_path}/RightMachineryCore",
            translation=(5.7, -4.75, 1.05),
            scale=(4.1, 1.25, 2.1),
            color=matte_black,
        )
        self._create_cube(
            prim_path=f"{self.props_path}/RightMachineryUpper",
            translation=(5.9, -4.75, 2.00),
            scale=(2.3, 0.8, 0.24),
            color=graphite,
        )
        self._create_cube(
            prim_path=f"{self.props_path}/RightMachineryBlue",
            translation=(5.7, -4.08, 1.60),
            scale=(2.8, 0.04, 0.04),
            color=electric_blue,
        )
        self._create_cube(
            prim_path=f"{self.props_path}/RightMachineryGold",
            translation=(5.7, -5.42, 1.22),
            scale=(1.7, 0.025, 0.03),
            color=premium_gold,
        )
    
    # rear service tower
        self._create_cube(
            prim_path=f"{self.props_path}/RearServiceTower",
            translation=(7.85, 4.35, 1.55),
            scale=(1.7, 1.3, 3.1),
            color=matte_black,
        )
        self._create_cube(
            prim_path=f"{self.props_path}/RearServiceTowerBlue",
            translation=(7.85, 3.72, 2.50),
            scale=(0.95, 0.04, 0.05),
            color=cyan_glow,
        )
        self._create_cube(
            prim_path=f"{self.props_path}/RearServiceTowerGold",
            translation=(7.20, 4.35, 2.05),
            scale=(0.03, 0.80, 0.04),
            color=premium_gold,
        )
   
    # sculpted front pillars
        self._create_cube(
            prim_path=f"{self.props_path}/FrontPillarLeft",
            translation=(-0.75, 5.45, 1.65),
            scale=(0.42, 0.42, 3.3),
            color=graphite,
        )
        self._create_cube(
            prim_path=f"{self.props_path}/FrontPillarLeftAccent",
            translation=(-0.75, 5.18, 2.45),
            scale=(0.10, 0.03, 0.04),
            color=electric_blue,
        )    

        self._create_cube(
            prim_path=f"{self.props_path}/FrontPillarRight",
            translation=(3.85, -5.45, 1.65),
            scale=(0.42, 0.42, 3.3),
            color=graphite,
        )
        self._create_cube(
            prim_path=f"{self.props_path}/FrontPillarRightAccent",
            translation=(3.85, -5.18, 2.45),
            scale=(0.10, 0.03, 0.04),
            color=electric_blue,
        )
    

    def _build_rover_placeholder(self):
        floor_top = self.scene_cfg.floor_size.z
        spawn = (0.0, 0.0, 0.0)

        self._ensure_xform(self.rover_path)

        rover_root = self.stage.GetPrimAtPath(self.rover_path)
        self._set_transform(
            rover_root,
            translation=(
                self.scene_cfg.deployment_zone.x,
                self.scene_cfg.deployment_zone.y,
                0.0,
            ),
        )

    # palette
        matte_black = (0.04, 0.04, 0.05)
        graphite_black = (0.09, 0.10, 0.12)
        deep_panel_black = (0.07, 0.08, 0.10)
        premium_gold = (0.72, 0.58, 0.22)
        dark_gold = (0.52, 0.40, 0.14)
        electric_blue = (0.00, 0.42, 0.95)
        cyan_glow = (0.20, 0.85, 1.00)
        wheel_black = (0.02, 0.02, 0.02)

    # main lower chassis
        self._create_cube(
            prim_path=f"{self.rover_path}/MainChassis",
            translation=(spawn[0], spawn[1], floor_top + 0.22),
            scale=(1.22, 0.72, 0.17),
            color=matte_black,
        )

    # upper shell
        self._create_cube(
            prim_path=f"{self.rover_path}/UpperShell",
            translation=(spawn[0], spawn[1], floor_top + 0.355),
            scale=(0.76, 0.44, 0.10),
            color=graphite_black,
        )

    # front nose
        self._create_cube(
            prim_path=f"{self.rover_path}/FrontNose",
            translation=(spawn[0] + 0.46, spawn[1], floor_top + 0.27),
            scale=(0.18, 0.46, 0.10),
            color=deep_panel_black,
        )

    # front sensor face
        self._create_cube(
            prim_path=f"{self.rover_path}/FrontSensorFace",
            translation=(spawn[0] + 0.57, spawn[1], floor_top + 0.30),
            scale=(0.05, 0.28, 0.09),
            color=electric_blue,
        )

    # front light blade
        self._create_cube(
            prim_path=f"{self.rover_path}/FrontLightStrip",
            translation=(spawn[0] + 0.60, spawn[1], floor_top + 0.20),
            scale=(0.02, 0.38, 0.03),
            color=cyan_glow,
        )

    # roof gold contour
        self._create_cube(
            prim_path=f"{self.rover_path}/RoofGoldContour",
            translation=(spawn[0] + 0.02, spawn[1], floor_top + 0.425),
            scale=(0.50, 0.03, 0.018),
            color=premium_gold,
        )

    # top blue signature
        self._create_cube(
            prim_path=f"{self.rover_path}/TopSignatureStrip",
            translation=(spawn[0] + 0.03, spawn[1], floor_top + 0.448),
            scale=(0.38, 0.025, 0.014),
            color=electric_blue,
        )

    # rear module
        self._create_cube(
            prim_path=f"{self.rover_path}/RearModule",
            translation=(spawn[0] - 0.46, spawn[1], floor_top + 0.31),
            scale=(0.18, 0.30, 0.13),
            color=deep_panel_black,
        )

    # rear gold trim
        self._create_cube(
            prim_path=f"{self.rover_path}/RearGoldTrim",
            translation=(spawn[0] - 0.55, spawn[1], floor_top + 0.36),
            scale=(0.02, 0.18, 0.03),
            color=dark_gold,
        )

    # side armor pods
        self._create_cube(
            prim_path=f"{self.rover_path}/LeftSidePod",
            translation=(spawn[0], spawn[1] + 0.37, floor_top + 0.22),
            scale=(0.78, 0.09, 0.11),
            color=deep_panel_black,
        )
        self._create_cube(
            prim_path=f"{self.rover_path}/RightSidePod",
            translation=(spawn[0], spawn[1] - 0.37, floor_top + 0.22),
            scale=(0.78, 0.09, 0.11),
            color=deep_panel_black,
        )

    # side contour lines
        self._create_cube(
            prim_path=f"{self.rover_path}/LeftGoldLine",
            translation=(spawn[0] + 0.02, spawn[1] + 0.415, floor_top + 0.27),
            scale=(0.62, 0.016, 0.024),
            color=dark_gold,
        )
        self._create_cube(
            prim_path=f"{self.rover_path}/RightGoldLine",
            translation=(spawn[0] + 0.02, spawn[1] - 0.415, floor_top + 0.27),
            scale=(0.62, 0.016, 0.024),
            color=dark_gold,
        )

        self._create_cube(
            prim_path=f"{self.rover_path}/LeftBlueLine",
            translation=(spawn[0] + 0.08, spawn[1] + 0.402, floor_top + 0.225),
            scale=(0.42, 0.012, 0.016),
            color=electric_blue,
        )
        self._create_cube(
            prim_path=f"{self.rover_path}/RightBlueLine",
            translation=(spawn[0] + 0.08, spawn[1] - 0.402, floor_top + 0.225),
            scale=(0.42, 0.012, 0.016),
            color=electric_blue,
        )

    # side skirts
        self._create_cube(
            prim_path=f"{self.rover_path}/LeftSkirt",
            translation=(spawn[0] - 0.02, spawn[1] + 0.30, floor_top + 0.13),
            scale=(0.92, 0.04, 0.05),
            color=matte_black,
        )
        self._create_cube(
            prim_path=f"{self.rover_path}/RightSkirt",
            translation=(spawn[0] - 0.02, spawn[1] - 0.30, floor_top + 0.13),
            scale=(0.92, 0.04, 0.05),
            color=matte_black,
        )

    # underbody glow
        self._create_cube(
            prim_path=f"{self.rover_path}/UnderbodyGlow",
            translation=(spawn[0] + 0.02, spawn[1], floor_top + 0.105),
            scale=(0.55, 0.045, 0.012),
            color=cyan_glow,
        )

    # sensor mast
        self._create_cube(
            prim_path=f"{self.rover_path}/SensorMast",
            translation=(spawn[0] - 0.06, spawn[1], floor_top + 0.58),
            scale=(0.04, 0.04, 0.24),
            color=(0.12, 0.13, 0.15),
        )

    # mast head
        self._create_cube(
            prim_path=f"{self.rover_path}/SensorHead",
            translation=(spawn[0] - 0.06, spawn[1], floor_top + 0.73),
            scale=(0.13, 0.10, 0.06),
            color=cyan_glow,
        )

        self._create_cube(
            prim_path=f"{self.rover_path}/SensorHeadTrim",
            translation=(spawn[0] - 0.06, spawn[1], floor_top + 0.685),
            scale=(0.10, 0.08, 0.014),
            color=premium_gold,
        )

    # omnidirectional / mecanum-style wheel modules
        wheel_modules = [
            ("FrontLeft",  (spawn[0] + 0.34, spawn[1] + 0.43, floor_top + 0.14)),
            ("FrontRight", (spawn[0] + 0.34, spawn[1] - 0.43, floor_top + 0.14)),
            ("RearLeft",   (spawn[0] - 0.34, spawn[1] + 0.43, floor_top + 0.14)),
            ("RearRight",  (spawn[0] - 0.34, spawn[1] - 0.43, floor_top + 0.14)),
        ]

        for name, wpos in wheel_modules:
            wx, wy, wz = wpos

            self._create_cylinder(
                prim_path=f"{self.rover_path}/{name}WheelBody",
                translation=(wx, wy, wz),
                radius=0.14,
                height=0.11,
                color=wheel_black,
                axis="Y",
            )

            self._create_cylinder(
                prim_path=f"{self.rover_path}/{name}WheelHub",
                translation=(wx, wy, wz),
                radius=0.05,
                height=0.035,
                color=dark_gold,
                axis="Y",
            )

            self._create_cylinder(
                prim_path=f"{self.rover_path}/{name}WheelRing",
                translation=(wx, wy, wz),
                radius=0.115,
                height=0.02,
                color=(0.10, 0.11, 0.13),
               axis="Y",
            )

            roller_sign = 1.0 if name in ("FrontLeft", "RearRight") else -1.0
            roller_offsets = [-0.085, -0.03, 0.03, 0.085]
            for ridx, roff in enumerate(roller_offsets):
                self._create_cube(
                    prim_path=f"{self.rover_path}/{name}Roller_{ridx}",
                    translation=(
                        wx + roller_sign * roff,
                        wy,
                        wz + roff * 0.45,
                    ),
                    scale=(0.035, 0.12, 0.018),
                    color=(0.16, 0.17, 0.19),
                )

            self._create_cube(
                prim_path=f"{self.rover_path}/{name}WheelAccent",
                translation=(wx, wy, wz - 0.13),
                scale=(0.05, 0.03, 0.02),
                color=electric_blue,
            )

    # wheel arch covers
        self._create_cube(
            prim_path=f"{self.rover_path}/FrontLeftArch",
            translation=(spawn[0] + 0.34, spawn[1] + 0.34, floor_top + 0.24),
            scale=(0.22, 0.08, 0.08),
            color=graphite_black,
        )
        self._create_cube(
            prim_path=f"{self.rover_path}/FrontRightArch",
            translation=(spawn[0] + 0.34, spawn[1] - 0.34, floor_top + 0.24),
            scale=(0.22, 0.08, 0.08),
            color=graphite_black,
        )
        self._create_cube(
            prim_path=f"{self.rover_path}/RearLeftArch",
            translation=(spawn[0] - 0.34, spawn[1] + 0.34, floor_top + 0.24),
            scale=(0.22, 0.08, 0.08),
            color=graphite_black,
        )
        self._create_cube(
            prim_path=f"{self.rover_path}/RearRightArch",
            translation=(spawn[0] - 0.34, spawn[1] - 0.34, floor_top + 0.24),
            scale=(0.22, 0.08, 0.08),
            color=graphite_black,
        )

    def _build_lights(self):
        matte_blue = self._Gf.Vec3f(0.08, 0.30, 0.95)
        cyan_glow = self._Gf.Vec3f(0.20, 0.85, 1.00)
        warm_gold = self._Gf.Vec3f(0.78, 0.60, 0.24)
        cool_white = self._Gf.Vec3f(0.86, 0.88, 0.94)
        soft_fill = self._Gf.Vec3f(0.62, 0.72, 0.95)

    # very soft ambient so the scene keeps contrast
        dome = self._UsdLux.DomeLight.Define(self.stage, f"{self.lights_path}/DomeLight")
        dome.CreateIntensityAttr(70.0)
        dome.CreateExposureAttr(0.0)
        dome.CreateColorAttr(self._Gf.Vec3f(0.58, 0.62, 0.72))

    # main hero key: keeps rover readable and premium
        hero = self._UsdLux.DistantLight.Define(self.stage, f"{self.lights_path}/HeroKey")
        hero.CreateIntensityAttr(2100.0)
        hero.CreateColorAttr(cool_white)

    # blue fill from front-left
        fill_blue = self._UsdLux.SphereLight.Define(self.stage, f"{self.lights_path}/FillBlue")
        fill_blue.CreateRadiusAttr(2.2)
        fill_blue.CreateIntensityAttr(9500.0)
        fill_blue.CreateColorAttr(matte_blue)
        self._set_transform(fill_blue.GetPrim(), translation=(-7.4, -5.6, 3.0))

    # cyan tech glow from upper-left, helps route and checkpoints pop
        cyan_side = self._UsdLux.SphereLight.Define(self.stage, f"{self.lights_path}/CyanSide")
        cyan_side.CreateRadiusAttr(1.8)
        cyan_side.CreateIntensityAttr(7000.0)
        cyan_side.CreateColorAttr(cyan_glow)
        self._set_transform(cyan_side.GetPrim(), translation=(-1.5, 6.2, 2.8))
   
    # warm gold rim from rear-right for luxury contrast
        gold_rim = self._UsdLux.SphereLight.Define(self.stage, f"{self.lights_path}/GoldRim")
        gold_rim.CreateRadiusAttr(1.8)
        gold_rim.CreateIntensityAttr(8200.0)
        gold_rim.CreateColorAttr(warm_gold)
        self._set_transform(gold_rim.GetPrim(), translation=(8.6, 5.7, 3.5))

    # rover hero light: focused product-demo lift
        rover_hero = self._UsdLux.SphereLight.Define(self.stage, f"{self.lights_path}/RoverHero")
        rover_hero.CreateRadiusAttr(1.1)
        rover_hero.CreateIntensityAttr(5200.0)
        rover_hero.CreateColorAttr(soft_fill)
        self._set_transform(rover_hero.GetPrim(), translation=(-8.1, 0.0, 2.1))

    # rear wall blue accent
        rear_blue = self._UsdLux.RectLight.Define(self.stage, f"{self.lights_path}/RearBlueAccent")
        rear_blue.CreateWidthAttr(4.0)
        rear_blue.CreateHeightAttr(1.2)
        rear_blue.CreateIntensityAttr(6000.0)
        rear_blue.CreateColorAttr(matte_blue)
        self._set_transform(rear_blue.GetPrim(), translation=(9.2, 0.0, 2.2))

    # subtle gold side accent to balance the palette
        side_gold = self._UsdLux.RectLight.Define(self.stage, f"{self.lights_path}/SideGoldAccent")
        side_gold.CreateWidthAttr(2.2)
        side_gold.CreateHeightAttr(0.8)
        side_gold.CreateIntensityAttr(3200.0)
        side_gold.CreateColorAttr(warm_gold)
        self._set_transform(side_gold.GetPrim(), translation=(6.8, -5.8, 1.8))

    # checkpoint wash to make the route read clearly from route/top cams
        route_cyan = self._UsdLux.RectLight.Define(self.stage, f"{self.lights_path}/RouteCyanWash")
        route_cyan.CreateWidthAttr(10.0)
        route_cyan.CreateHeightAttr(1.6)
        route_cyan.CreateIntensityAttr(2600.0)
        route_cyan.CreateColorAttr(cyan_glow)
        self._set_transform(route_cyan.GetPrim(), translation=(0.0, 0.0, 3.2))

    def _build_cameras(self):
    # delayed imports because this runs after SimulationApp startup
        import math

        self._late_imports()

        def set_camera_transform(camera_prim, translate, rotate_xyz_deg):
            xform = self._UsdGeom.Xformable(camera_prim)
  
            translate_op = None
            rotate_op = None

            for op in xform.GetOrderedXformOps():
                if op.GetOpType() == self._UsdGeom.XformOp.TypeTranslate:
                    translate_op = op
                elif op.GetOpType() == self._UsdGeom.XformOp.TypeRotateXYZ:
                    rotate_op = op

            if translate_op is None:
                translate_op = xform.AddTranslateOp()
            if rotate_op is None:
                rotate_op = xform.AddRotateXYZOp()

            translate_op.Set(self._Gf.Vec3d(*translate))
            rotate_op.Set(self._Gf.Vec3f(*rotate_xyz_deg))

    # Hero camera: premium front three-quarter shot
        hero_cam = self._UsdGeom.Camera.Define(self.stage, f"{self.cameras_path}/HeroCamera")
        set_camera_transform(
            hero_cam.GetPrim(),
            translate=(-11.2, -6.8, 4.4),
            rotate_xyz_deg=(58.0, 0.0, -32.0),
        )
        hero_cam.CreateFocalLengthAttr(32.0)
        hero_cam.CreateFocusDistanceAttr(18.0)
        hero_cam.CreateClippingRangeAttr(self._Gf.Vec2f(0.01, 1000.0))

    # Route camera: cleaner elevated route view
        route_cam = self._UsdGeom.Camera.Define(self.stage, f"{self.cameras_path}/RouteCamera")
        set_camera_transform(
            route_cam.GetPrim(),
            translate=(-1.5, -13.5, 8.2),
            rotate_xyz_deg=(63.0, 0.0, -8.0),
        )
        route_cam.CreateFocalLengthAttr(28.0)
        route_cam.CreateFocusDistanceAttr(25.0)
        route_cam.CreateClippingRangeAttr(self._Gf.Vec2f(0.01, 1000.0))

    # Top documentation camera
        top_cam = self._UsdGeom.Camera.Define(self.stage, f"{self.cameras_path}/TopCamera")
        set_camera_transform(
            top_cam.GetPrim(),
            translate=(0.0, 0.0, 20.0),
            rotate_xyz_deg=(0.0, 0.0, 0.0),
        )
        top_cam.CreateFocalLengthAttr(20.0)
        top_cam.CreateFocusDistanceAttr(30.0)
        top_cam.CreateClippingRangeAttr(self._Gf.Vec2f(0.01, 1000.0))
    def set_active_camera(self, camera_prim_path: str = "/World/AegisInspectionBay/Cameras/HeroCamera"):
        import omni.kit.viewport.utility as viewport_utility

        viewport = viewport_utility.get_active_viewport()
        if viewport is None:
            print("[WARN] No active viewport found. Camera not switched.")
            return

        viewport.camera_path = camera_prim_path
        print(f"[CAMERA] Active viewport camera set to: {camera_prim_path}")
    def animate_hero_camera_pullback(
        self,
        step_count: int,
        start_step: int = 0,
        end_step: int = 180,
        start_pos=(-9.2, -5.2, 3.2),
        end_pos=(-12.8, -8.0, 5.6),
        camera_prim_path: str = "/World/AegisInspectionBay/Cameras/HeroCamera",
    ):
        if step_count < start_step:
            return
        if step_count > end_step:
            step_count = end_step

        t = (step_count - start_step) / max((end_step - start_step), 1)

    # smoothstep easing for more cinematic motion
        t = t * t * (3.0 - 2.0 * t)

        x = start_pos[0] + (end_pos[0] - start_pos[0]) * t
        y = start_pos[1] + (end_pos[1] - start_pos[1]) * t
        z = start_pos[2] + (end_pos[2] - start_pos[2]) * t

        from pxr import Gf, UsdGeom
        import omni.usd

        stage = omni.usd.get_context().get_stage()
        camera_prim = stage.GetPrimAtPath(camera_prim_path)
        if not camera_prim:
            return

        xform = UsdGeom.Xformable(camera_prim)

        translate_op = None
        rotate_op = None

        for op in xform.GetOrderedXformOps():
            if op.GetOpType() == UsdGeom.XformOp.TypeTranslate:
                translate_op = op
            elif op.GetOpType() == UsdGeom.XformOp.TypeRotateXYZ:
                rotate_op = op

        if translate_op is None:
            translate_op = xform.AddTranslateOp()
        if rotate_op is None:
            rotate_op = xform.AddRotateXYZOp()

        translate_op.Set(Gf.Vec3d(x, y, z))
        rotate_op.Set(Gf.Vec3f(58.0, 0.0, -32.0))
        