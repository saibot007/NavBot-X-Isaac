from __future__ import annotations

import math


class RoverController:
    def __init__(self, rover_prim_path: str = "/World/AegisInspectionBay/NavBotXRover"):
        self.rover_prim_path = rover_prim_path
        self.current_yaw_deg = 0.0

    def _get_rover_prim(self):
        import omni.usd

        stage = omni.usd.get_context().get_stage()
        prim = stage.GetPrimAtPath(self.rover_prim_path)
        if not prim:
            raise RuntimeError(f"Rover prim not found at {self.rover_prim_path}")
        return prim

    def _get_xform_ops(self, prim):
        from pxr import UsdGeom

        xform = UsdGeom.Xformable(prim)

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

        return translate_op, rotate_op

    def get_position(self):
        prim = self._get_rover_prim()
        translate_op, _ = self._get_xform_ops(prim)
        pos = translate_op.Get()
        return (float(pos[0]), float(pos[1]), float(pos[2]))

    def get_yaw_deg(self):
        prim = self._get_rover_prim()
        _, rotate_op = self._get_xform_ops(prim)
        rot = rotate_op.Get()

        if rot is None:
            self.current_yaw_deg = 0.0
            return self.current_yaw_deg

        self.current_yaw_deg = float(rot[2])
        return self.current_yaw_deg

    def set_pose(self, position, yaw_deg: float):
        from pxr import Gf

        prim = self._get_rover_prim()
        translate_op, rotate_op = self._get_xform_ops(prim)

        translate_op.Set(Gf.Vec3d(*position))
        rotate_op.Set(Gf.Vec3f(0.0, 0.0, yaw_deg))
        self.current_yaw_deg = yaw_deg

    def set_yaw_deg(self, yaw_deg: float):
        x, y, z = self.get_position()
        self.set_pose((x, y, z), yaw_deg)

    def hold_position(self):
        x, y, z = self.get_position()
        self.set_pose((x, y, z), self.get_yaw_deg())

    def move_toward(
        self,
        target_pos,
        max_speed: float = 0.035,
        reach_thresh: float = 0.08,
        yaw_lerp: float = 0.18,
    ):
        x, y, z = self.get_position()
        tx, ty, tz = target_pos

        dx = tx - x
        dy = ty - y
        dist_xy = math.sqrt(dx * dx + dy * dy)

        if dist_xy <= reach_thresh:
            desired_yaw = math.degrees(math.atan2(dy, dx)) if dist_xy > 1e-6 else self.get_yaw_deg()
            self.set_pose((tx, ty, z), desired_yaw)
            return True

        vx = (dx / dist_xy) * max_speed
        vy = (dy / dist_xy) * max_speed

        nx = x + vx
        ny = y + vy

        desired_yaw = math.degrees(math.atan2(dy, dx))
        current_yaw = self.get_yaw_deg() if self.get_yaw_deg() is not None else 0.0
        new_yaw = current_yaw + (desired_yaw - current_yaw) * yaw_lerp

        self.set_pose((nx, ny, z), new_yaw)
        return False