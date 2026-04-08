from __future__ import annotations

import math

from navbot_x_isaac_lab.demo.scene_config import AegisInspectionBayConfig


class CheckpointManager:
    def __init__(self, scene_cfg: AegisInspectionBayConfig | None = None):
        self.scene_cfg = scene_cfg if scene_cfg is not None else AegisInspectionBayConfig()

        self.checkpoints = {
            "A": (
                self.scene_cfg.checkpoints[0].position.x,
                self.scene_cfg.checkpoints[0].position.y,
                0.0,
            ),
            "B": (
                self.scene_cfg.checkpoints[1].position.x,
                self.scene_cfg.checkpoints[1].position.y,
                0.0,
            ),
            "C": (
                self.scene_cfg.checkpoints[2].position.x,
                self.scene_cfg.checkpoints[2].position.y,
                0.0,
            ),
        }

        self.hero_end_pose = (
            self.scene_cfg.hero_end_pose.x,
            self.scene_cfg.hero_end_pose.y,
            0.0,
        )

    def get_checkpoint_position(self, name: str):
        return self.checkpoints[name]

    def get_hero_end_position(self):
        return self.hero_end_pose

    def is_at_position(self, rover_pos, target_pos, thresh: float = 0.12):
        rx, ry, _ = rover_pos
        tx, ty, _ = target_pos
        dist = math.sqrt((tx - rx) ** 2 + (ty - ry) ** 2)
        return dist <= thresh