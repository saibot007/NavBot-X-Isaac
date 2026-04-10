from __future__ import annotations

from dataclasses import dataclass


@dataclass
class InspectionRLEnvCfg:
    max_steps: int = 1300

    move_speed: float = 0.022
    turn_speed_deg: float = 1.6
    action_smoothing: float = 0.94

    reach_threshold: float = 0.26
    out_of_bounds_x: float = 12.0
    out_of_bounds_y: float = 7.0

    progress_reward_scale: float = 10.0
    stage2_progress_scale: float = 1.35
    stage3_progress_scale: float = 1.8
    step_penalty: float = 0.01
    yaw_penalty_scale: float = 0.0025
    heading_alignment_reward: float = 0.008
    large_heading_penalty_scale: float = 0.006

    goal_bonus: float = 40.0
    stage1_bonus: float = 4.0
    stage2_bonus: float = 6.0
    out_of_bounds_penalty: float = 5.0