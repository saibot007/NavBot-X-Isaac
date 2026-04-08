from __future__ import annotations


class StatusVisualizer:
    def __init__(self):
        self.last_state = None

    def log_state_change(self, state: str):
        if state != self.last_state:
            print(f"[TASK STATE] {state}")
            self.last_state = state

    def set_checkpoint_highlight(self, checkpoint_name: str | None):
        from pxr import Gf, UsdGeom
        import omni.usd

        stage = omni.usd.get_context().get_stage()

        checkpoint_map = {
            "A": [
                "/World/AegisInspectionBay/Checkpoints/CheckpointABase",
                "/World/AegisInspectionBay/Checkpoints/CheckpointAGlow",
                "/World/AegisInspectionBay/Checkpoints/CheckpointABeacon",
                "/World/AegisInspectionBay/Checkpoints/CheckpointATopCap",
            ],
            "B": [
                "/World/AegisInspectionBay/Checkpoints/CheckpointBBase",
                "/World/AegisInspectionBay/Checkpoints/CheckpointBGlow",
                "/World/AegisInspectionBay/Checkpoints/CheckpointBBeacon",
                "/World/AegisInspectionBay/Checkpoints/CheckpointBTopCap",
            ],
            "C": [
                "/World/AegisInspectionBay/Checkpoints/CheckpointCBase",
                "/World/AegisInspectionBay/Checkpoints/CheckpointCGlow",
                "/World/AegisInspectionBay/Checkpoints/CheckpointCBeacon",
                "/World/AegisInspectionBay/Checkpoints/CheckpointCTopCap",
            ],
        }

        active_color = Gf.Vec3f(0.95, 0.75, 0.22)
        inactive_glow = Gf.Vec3f(0.18, 0.85, 1.00)
        inactive_dark = Gf.Vec3f(0.05, 0.06, 0.08)

        for key, prim_paths in checkpoint_map.items():
            for prim_path in prim_paths:
                prim = stage.GetPrimAtPath(prim_path)
                if not prim:
                    continue

                gprim = UsdGeom.Gprim(prim)
                if key == checkpoint_name:
                    gprim.CreateDisplayColorAttr([active_color])
                else:
                    if "Glow" in prim_path or "Beacon" in prim_path or "TopCap" in prim_path:
                        gprim.CreateDisplayColorAttr([inactive_glow])
                    else:
                        gprim.CreateDisplayColorAttr([inactive_dark])