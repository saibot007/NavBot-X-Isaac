from __future__ import annotations

from navbot_x_isaac_lab.demo.rover_controller import RoverController


class GestureController:
    def __init__(self, rover_prim_path: str = "/World/AegisInspectionBay/NavBotXRover"):
        self.controller = RoverController(rover_prim_path=rover_prim_path)
        self.step_size = 0.035
        self.turn_step_deg = 4.0

    def update(self, command: str):
        x, y, z = self.controller.get_position()
        yaw = self.controller.get_yaw_deg()

        if command == "STOP":
            self.controller.hold_position()
            return

        if command == "LEFT":
            self.controller.set_yaw_deg(yaw + self.turn_step_deg)
            return

        if command == "RIGHT":
            self.controller.set_yaw_deg(yaw - self.turn_step_deg)
            return

        import math

        yaw_rad = math.radians(yaw)
        forward_dx = math.cos(yaw_rad) * self.step_size
        forward_dy = math.sin(yaw_rad) * self.step_size

        if command == "FORWARD":
            self.controller.set_pose((x + forward_dx, y + forward_dy, z), yaw)
            return

        if command == "BACKWARD":
            self.controller.set_pose((x - forward_dx, y - forward_dy, z), yaw)
            return

        self.controller.hold_position()