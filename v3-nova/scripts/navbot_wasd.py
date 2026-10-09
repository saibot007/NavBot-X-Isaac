#!/usr/bin/env python3

import sys
import termios
import tty
import rclpy

from rclpy.node import Node
from geometry_msgs.msg import Twist


class NavBotTeleop(Node):

    def __init__(self):
        super().__init__('navbot_wasd')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)

    def send(self, linear=0.0, angular=0.0):
        msg = Twist()
        msg.linear.x = linear
        msg.angular.z = angular

        # Send several times so Isaac reliably receives it
        for _ in range(5):
            self.pub.publish(msg)
            rclpy.spin_once(self, timeout_sec=0.02)

    def stop(self):
        self.send(0.0, 0.0)


def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)

    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

    return key


def main():

    rclpy.init()
    node = NavBotTeleop()

    print("""
==============================
      NAVBOT-X CONTROL
==============================

W  = Forward
S  = Backward
A  = Turn Left
D  = Turn Right

SPACE = Stop
Q     = Quit

==============================
""")

    try:

        while rclpy.ok():

            key = get_key().lower()

            if key == 'w':
                node.send(linear=0.25)
                print("FORWARD")

            elif key == 's':
                node.send(linear=-0.20)
                print("BACKWARD")

            elif key == 'a':
                node.send(angular=0.5)
                print("TURN LEFT")

            elif key == 'd':
                node.send(angular=-0.5)
                print("TURN RIGHT")

            elif key == ' ':
                node.stop()
                print("STOP")

            elif key == 'q':
                node.stop()
                print("EXIT")
                break

    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
