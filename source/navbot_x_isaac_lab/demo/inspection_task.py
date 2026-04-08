from __future__ import annotations

from navbot_x_isaac_lab.demo.checkpoint_manager import CheckpointManager
from navbot_x_isaac_lab.demo.rover_controller import RoverController
from navbot_x_isaac_lab.demo.scene_config import AegisInspectionBayConfig
from navbot_x_isaac_lab.demo.status_visualizer import StatusVisualizer


class InspectionTask:
    def __init__(
        self,
        rover_prim_path: str = "/World/AegisInspectionBay/NavBotXRover",
        hold_seconds: float = 0.5,
        sim_fps: float = 60.0,
    ):
        self.scene_cfg = AegisInspectionBayConfig()
        self.controller = RoverController(rover_prim_path=rover_prim_path)
        self.checkpoints = CheckpointManager(scene_cfg=self.scene_cfg)
        self.visualizer = StatusVisualizer()

        self.state = "GO_TO_A"
        self.hold_frames = int(hold_seconds * sim_fps)
        self.hold_counter = 0

        self.scan_center_yaw = 0.0

        self.scan_a_left = 18.0
        self.scan_a_right = -18.0

        self.scan_b_left = 30.0
        self.scan_b_right = -30.0

        self.scan_c_left = 20.0
        self.scan_c_right = -20.0
    def _update_visual_state(self):
        self.visualizer.log_state_change(self.state)

        if "A" in self.state:
            self.visualizer.set_checkpoint_highlight("A")
        elif "B" in self.state:
            self.visualizer.set_checkpoint_highlight("B")
        elif "C" in self.state:
            self.visualizer.set_checkpoint_highlight("C")
        else:
            self.visualizer.set_checkpoint_highlight(None)    

    def _hold_and_advance(self, next_state: str):
        self.controller.hold_position()
        self.hold_counter += 1
        if self.hold_counter >= self.hold_frames:
            self.hold_counter = 0
            self.state = next_state

    def _scan_step(self, yaw_deg: float, next_state: str):
        self.controller.set_yaw_deg(yaw_deg)
        self.hold_counter += 1
        if self.hold_counter >= self.hold_frames:
            self.hold_counter = 0
            self.state = next_state

    def update(self):

        self._update_visual_state()
        if self.state == "GO_TO_A":
            reached = self.controller.move_toward(
                self.checkpoints.get_checkpoint_position("A"),
                max_speed=0.034,
                reach_thresh=0.10,
                yaw_lerp=0.18,
            )
            if reached:
                self.scan_center_yaw = self.controller.get_yaw_deg()
                self.state = "SCAN_A_LEFT"

        elif self.state == "SCAN_A_LEFT":
            self._scan_step(self.scan_center_yaw + self.scan_a_left, "SCAN_A_RIGHT")

        elif self.state == "SCAN_A_RIGHT":
            self._scan_step(self.scan_center_yaw + self.scan_a_right, "SCAN_A_CENTER")

        elif self.state == "SCAN_A_CENTER":
            self._scan_step(self.scan_center_yaw, "GO_TO_B")

        elif self.state == "GO_TO_B":
            reached = self.controller.move_toward(
                self.checkpoints.get_checkpoint_position("B"),
                max_speed=0.030,
                reach_thresh=0.10,
                yaw_lerp=0.16,
            )
            if reached:
                self.scan_center_yaw = self.controller.get_yaw_deg()
                self.state = "SCAN_B_LEFT"

        elif self.state == "SCAN_B_LEFT":
            self._scan_step(self.scan_center_yaw + self.scan_b_left, "SCAN_B_RIGHT")

        elif self.state == "SCAN_B_RIGHT":
            self._scan_step(self.scan_center_yaw + self.scan_b_right, "SCAN_B_CENTER")

        elif self.state == "SCAN_B_CENTER":
            self._scan_step(self.scan_center_yaw, "GO_TO_C")

        elif self.state == "GO_TO_C":
            reached = self.controller.move_toward(
                self.checkpoints.get_checkpoint_position("C"),
                max_speed=0.026,
                reach_thresh=0.10,
                yaw_lerp=0.14,
            )
            if reached:
                self.scan_center_yaw = self.controller.get_yaw_deg()
                self.state = "SCAN_C_LEFT"

        elif self.state == "SCAN_C_LEFT":
            self._scan_step(self.scan_center_yaw + self.scan_c_left, "SCAN_C_CENTER_1")

        elif self.state == "SCAN_C_CENTER_1":
            self._scan_step(self.scan_center_yaw, "SCAN_C_RIGHT")

        elif self.state == "SCAN_C_RIGHT":
            self._scan_step(self.scan_center_yaw + self.scan_c_right, "SCAN_C_CENTER_2")

        elif self.state == "SCAN_C_CENTER_2":
            self._scan_step(self.scan_center_yaw, "RETURN_HERO")

        elif self.state == "RETURN_HERO":
            reached = self.controller.move_toward(
                self.checkpoints.get_hero_end_position(),
                max_speed=0.036,
                reach_thresh=0.10,
                yaw_lerp=0.18,
            )
            if reached:
                self.state = "COMPLETE"

        elif self.state == "COMPLETE":
            self.controller.hold_position() 

    def _update_visual_state(self):
        self.visualizer.log_state_change(self.state)

        if "A" in self.state:
            self.visualizer.set_checkpoint_highlight("A")
        elif "B" in self.state:
            self.visualizer.set_checkpoint_highlight("B")
        elif "C" in self.state:
            self.visualizer.set_checkpoint_highlight("C")
        else:
            self.visualizer.set_checkpoint_highlight(None)        