from __future__ import annotations

import math


class RouteAnimator:
    """Phase-1 flagship motion layer for NavBot-X Rover.

    This version uses omnidirectional-style movement:
    - smooth translation
    - deliberate lateral inspection offsets
    - controlled body heading
    """

    def __init__(self, rover_prim_path: str = "/World/AegisInspectionBay/NavBotXRover"):
        self.rover_prim_path = rover_prim_path

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

    def move_segment(
        self,
        start_pos,
        end_pos,
        steps: int = 120,
        pause: float = 0.0,
        heading_mode: str = "fixed",
        heading_deg: float = 0.0,
    ):
        from pxr import Gf

        prim = self._get_rover_prim()
        translate_op, rotate_op = self._get_xform_ops(prim)

        sx, sy, sz = start_pos
        ex, ey, ez = end_pos

        dx = ex - sx
        dy = ey - sy
        dz = ez - sz

        if heading_mode == "path":
            computed_heading = math.degrees(math.atan2(dy, dx))
        else:
            computed_heading = heading_deg

        for i in range(steps + 1):
            t = i / steps
            x = sx + dx * t
            y = sy + dy * t
            z = sz + dz * t

            translate_op.Set(Gf.Vec3d(x, y, z))
            rotate_op.Set(Gf.Vec3f(0.0, 0.0, computed_heading))
            yield

        if pause > 0:
            pause_steps = int(pause * 60)
            for _ in range(pause_steps):
                yield

    def inspection_route_alpha(self):
        z = 0.0

        # Omni-style flagship inspection route:
        # rover stays mostly facing forward (0 deg)
        # while making controlled lateral inspection offsets.
        segments = [
            # deploy forward off the pad
            ((-8.0,  0.0, z), (-6.0,  0.0, z), 100, 0.15, "fixed", 0.0),

            # lateral inspection shift toward Checkpoint A zone
            ((-6.0,  0.0, z), (-4.3,  0.55, z), 95, 0.25, "fixed", 0.0),

            # return closer to center lane
            ((-4.3,  0.55, z), (-2.2,  0.10, z), 95, 0.15, "fixed", 0.0),

            # slight negative offset for checkpoint B style pass
            ((-2.2,  0.10, z), ( 1.0, -0.35, z), 120, 0.25, "fixed", 0.0),

            # recenter and continue
            (( 1.0, -0.35, z), ( 4.3,  0.05, z), 120, 0.15, "fixed", 0.0),

            # final clean approach
            (( 4.3,  0.05, z), ( 8.2,  0.0, z), 130, 0.60, "fixed", 0.0),
        ]

        for start, end, steps, pause, heading_mode, heading_deg in segments:
            for _ in self.move_segment(
                start,
                end,
                steps=steps,
                pause=pause,
                heading_mode=heading_mode,
                heading_deg=heading_deg,
            ):
                yield