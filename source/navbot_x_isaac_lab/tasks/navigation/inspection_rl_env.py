from __future__ import annotations

import math
import numpy as np

from navbot_x_isaac_lab.demo.rover_controller import RoverController
from navbot_x_isaac_lab.demo.scene_config import AegisInspectionBayConfig
from navbot_x_isaac_lab.tasks.navigation.inspection_rl_env_cfg import InspectionRLEnvCfg


class InspectionRLEnv:
    def __init__(self, cfg: InspectionRLEnvCfg | None = None):
        self.cfg = cfg if cfg is not None else InspectionRLEnvCfg()

        self.scene_cfg = AegisInspectionBayConfig()
        self.controller = RoverController("/World/AegisInspectionBay/NavBotXRover")

        self.max_steps = self.cfg.max_steps
        self.step_count = 0

        self.spawn = (
            self.scene_cfg.deployment_zone.x,
            self.scene_cfg.deployment_zone.y,
            0.0,
        )

        self.targets = [
            (
                self.scene_cfg.checkpoints[0].position.x,
                self.scene_cfg.checkpoints[0].position.y,
                0.0,
            ),
            (
                self.scene_cfg.checkpoints[1].position.x,
                self.scene_cfg.checkpoints[1].position.y,
                0.0,
            ),
            (
                self.scene_cfg.checkpoints[2].position.x,
                self.scene_cfg.checkpoints[2].position.y,
                0.0,
            ),
        ]
        self.target_names = ["Checkpoint A", "Checkpoint B", "Checkpoint C"]

        self.target_index = 0
        self.target = self.targets[self.target_index]

        self.prev_distance = None
        self.prev_action = np.zeros(2, dtype=np.float32)
        self.action_smoothing = self.cfg.action_smoothing

    def _get_current_target(self):
        return self.targets[self.target_index]

    def _distance_to_current_target(self):
        x, y, _ = self.controller.get_position()
        tx, ty, _ = self._get_current_target()
        return math.sqrt((tx - x) ** 2 + (ty - y) ** 2)

    def _get_obs(self):
        x, y, _ = self.controller.get_position()
        yaw_deg = self.controller.get_yaw_deg()

        tx, ty, _ = self._get_current_target()
        dx = tx - x
        dy = ty - y
        dist = math.sqrt(dx * dx + dy * dy)

        target_heading = math.degrees(math.atan2(dy, dx))
        heading_error = target_heading - yaw_deg

        while heading_error > 180.0:
            heading_error -= 360.0
        while heading_error < -180.0:
            heading_error += 360.0

        stage_progress = 0.0
        if len(self.targets) > 1:
            stage_progress = self.target_index / float(len(self.targets) - 1)

        return np.array(
            [
                x / 12.0,
                y / 7.0,
                dx / 12.0,
                dy / 7.0,
                dist / 15.0,
                yaw_deg / 180.0,
                heading_error / 180.0,
                stage_progress,
            ],
            dtype=np.float32,
        )

    def reset(self):
        self.step_count = 0
        self.target_index = 0
        self.target = self.targets[self.target_index]

        self.controller.set_pose(self.spawn, 0.0)
        self.prev_distance = self._distance_to_current_target()
        self.prev_action[:] = 0.0
        return self._get_obs()

    def step(self, action):
        self.step_count += 1

        x, y, z = self.controller.get_position()
        yaw_deg = self.controller.get_yaw_deg()

        raw_action = np.clip(np.asarray(action, dtype=np.float32), -1.0, 1.0)
        smoothed_action = (
            self.action_smoothing * self.prev_action
            + (1.0 - self.action_smoothing) * raw_action
        )
        self.prev_action = smoothed_action.copy()

        forward_cmd = max(0.0, float(smoothed_action[0]))
        yaw_cmd = float(smoothed_action[1])

        tx, ty, _ = self._get_current_target()
        new_yaw = yaw_deg + yaw_cmd * self.cfg.turn_speed_deg

        target_heading = math.degrees(math.atan2(ty - y, tx - x))
        heading_error = target_heading - new_yaw

        while heading_error > 180.0:
            heading_error -= 360.0
        while heading_error < -180.0:
            heading_error += 360.0

        if abs(heading_error) > 60.0:
            forward_cmd *= 0.02
        elif abs(heading_error) > 35.0:
            forward_cmd *= 0.12
        elif abs(heading_error) > 20.0:
            forward_cmd *= 0.30

        yaw_rad = math.radians(new_yaw)

        nx = x + math.cos(yaw_rad) * forward_cmd * self.cfg.move_speed
        ny = y + math.sin(yaw_rad) * forward_cmd * self.cfg.move_speed

        self.controller.set_pose((nx, ny, z), new_yaw)

        dist = self._distance_to_current_target()
        progress = self.prev_distance - dist
        self.prev_distance = dist

        stage_progress_scale = 1.0
        if self.target_index == 1:
            stage_progress_scale = self.cfg.stage2_progress_scale
        elif self.target_index == 2:
            stage_progress_scale = self.cfg.stage3_progress_scale

        reward = 0.0
        reward += progress * self.cfg.progress_reward_scale * stage_progress_scale
        reward -= self.cfg.step_penalty
        reward -= self.cfg.yaw_penalty_scale * abs(yaw_cmd)
        reward += self.cfg.heading_alignment_reward * (1.0 - abs(heading_error) / 180.0)
        reward -= self.cfg.large_heading_penalty_scale * max(
            0.0, (abs(heading_error) - 45.0) / 135.0
        )

        terminated = False
        truncated = False
        reached_stage_target = False
        mission_success = False
        stage_bonus = 0.0

        if dist < self.cfg.reach_threshold:
            reached_stage_target = True

            if self.target_index < len(self.targets) - 1:
                if self.target_index == 0:
                    stage_bonus = self.cfg.stage1_bonus
                else:
                    stage_bonus = self.cfg.stage2_bonus

                reward += stage_bonus

                self.target_index += 1
                self.target = self.targets[self.target_index]
                self.prev_distance = self._distance_to_current_target()
            else:
                reward += self.cfg.goal_bonus
                mission_success = True
                terminated = True

        if abs(nx) > self.cfg.out_of_bounds_x or abs(ny) > self.cfg.out_of_bounds_y:
            reward -= self.cfg.out_of_bounds_penalty
            terminated = True

        if self.step_count >= self.max_steps:
            truncated = True

        obs = self._get_obs()
        info = {
            "distance_to_target": dist,
            "success": mission_success,
            "heading_error_deg": heading_error,
            "target_index": self.target_index,
            "target_name": self.target_names[self.target_index],
            "reached_stage_target": reached_stage_target,
            "mission_stage": self.target_index + 1,
            "stage_bonus": stage_bonus,
        }

        return obs, reward, terminated, truncated, info