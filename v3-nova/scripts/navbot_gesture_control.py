
#!/usr/bin/env python3
"""NavBot-X V3 Gesture Controller — ROS 2 Jazzy."""

import time
from pathlib import Path

import cv2
import mediapipe as mp
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


# ===== CONFIGURATION =====

MODEL_CANDIDATES = [
    Path(__file__).resolve().parent.parent / "models" / "gesture_recognizer.task",
    Path.home() / "navbot_gesture_models" / "gesture_recognizer.task",
]

CONFIDENCE_THRESHOLD = 0.60
HAND_TIMEOUT = 0.50

FORWARD_SPEED = 0.25      # m/s
REVERSE_SPEED = 0.15      # m/s
TURN_SPEED = 0.60         # rad/s

LEFT_ZONE = 0.35
RIGHT_ZONE = 0.65

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17)
]


# ===== ROS 2 CONTROLLER =====

class GestureController(Node):

    def __init__(self):
        super().__init__("navbot_gesture_controller")

        self.pub = self.create_publisher(
            Twist, "/cmd_vel_gesture", 10
        )

        self.mode = "AUTO"
        self.last_manual_time = time.monotonic()

    def publish_cmd(self, linear=0.0, angular=0.0):
        msg = Twist()
        msg.linear.x = float(linear)
        msg.angular.z = float(angular)
        self.pub.publish(msg)


# ===== MODEL LOADING =====

def find_model():
    for path in MODEL_CANDIDATES:
        if path.is_file():
            return str(path)

    raise FileNotFoundError(
        "Gesture model not found. Download gesture_recognizer.task."
    )


# ===== HAND VISUALIZATION =====

def draw_hand_landmarks(frame, result):

    if not result.hand_landmarks:
        return

    height, width = frame.shape[:2]

    for hand in result.hand_landmarks:

        points = [
            (int(lm.x * width), int(lm.y * height))
            for lm in hand
        ]

        # Green finger connections
        for start, end in HAND_CONNECTIONS:
            cv2.line(
                frame,
                points[start],
                points[end],
                (0, 255, 0),
                2
            )

        # Red joint markers
        for point in points:
            cv2.circle(
                frame,
                point,
                4,
                (0, 0, 255),
                -1
            )


# ===== MAIN APPLICATION =====

def main():

    rclpy.init()
    node = GestureController()

    cap = None
    recognizer = None

    try:
        options = mp.tasks.vision.GestureRecognizerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path=find_model()
            ),
            running_mode=mp.tasks.vision.RunningMode.IMAGE,
            num_hands=1,
        )

        recognizer = (
            mp.tasks.vision.GestureRecognizer.create_from_options(
                options
            )
        )

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            raise RuntimeError("Cannot open webcam")

        print("""
========================================
       NAVBOT-X GESTURE CONTROL
========================================

POINTING UP (CENTER) = MOVE FORWARD
POINTING UP (LEFT)   = TURN LEFT
POINTING UP (RIGHT)  = TURN RIGHT

THUMB DOWN           = MOVE BACKWARD

OPEN PALM            = STOP
CLOSED FIST          = STOP

VICTORY              = AUTONOMOUS MODE

Q                    = QUIT
========================================
""")

        while rclpy.ok():

            ok, frame = cap.read()

            if not ok:
                if node.mode == "MANUAL":
                    node.mode = "STOP"

                if node.mode == "STOP":
                    node.publish_cmd(0.0, 0.0)

                rclpy.spin_once(node, timeout_sec=0.001)
                time.sleep(0.03)
                continue

            # Mirror webcam
            frame = cv2.flip(frame, 1)

            rgb = cv2.cvtColor(
                frame, cv2.COLOR_BGR2RGB
            )

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb
            )

            result = recognizer.recognize(mp_image)

            # Draw hand skeleton
            draw_hand_landmarks(frame, result)

            # Default values
            gesture = "No hand"
            score = 0.0
            finger_x = 0.5
            valid = False

            if result.gestures and result.hand_landmarks:

                best = result.gestures[0][0]

                gesture = best.category_name
                score = float(best.score)

                finger_x = result.hand_landmarks[0][8].x

                valid = score >= CONFIDENCE_THRESHOLD

            linear = 0.0
            angular = 0.0

            action = (
                "AUTONOMOUS MODE"
                if node.mode == "AUTO"
                else "STOPPED"
            )

            manual_command = False

            # ===== STOP =====

            if valid and gesture in (
                "Open_Palm", "Closed_Fist"
            ):
                node.mode = "STOP"
                action = "STOPPED"

            # ===== AUTONOMOUS MODE =====

            elif valid and gesture == "Victory":

                if node.mode != "AUTO":
                    # Stop before releasing gesture control
                    node.publish_cmd(0.0, 0.0)

                node.mode = "AUTO"
                action = "AUTONOMOUS MODE"

            # ===== FORWARD / LEFT / RIGHT =====

            elif valid and gesture == "Pointing_Up":

                node.mode = "MANUAL"
                manual_command = True
                node.last_manual_time = time.monotonic()

                if finger_x < LEFT_ZONE:

                    linear = 0.0
                    angular = TURN_SPEED
                    action = "TURNING LEFT"

                elif finger_x > RIGHT_ZONE:

                    linear = 0.0
                    angular = -TURN_SPEED
                    action = "TURNING RIGHT"

                else:

                    linear = FORWARD_SPEED
                    angular = 0.0
                    action = "MOVING FORWARD"

            # ===== BACKWARD (CORRECTED) =====

            elif valid and gesture == "Thumb_Down":

                node.mode = "MANUAL"
                manual_command = True
                node.last_manual_time = time.monotonic()

                # Negative linear.x = reverse
                linear = -REVERSE_SPEED
                angular = 0.0

                action = "MOVING BACKWARD"

            # ===== SAFETY & PUBLISHING =====

            if node.mode == "STOP":

                node.publish_cmd(0.0, 0.0)
                linear = 0.0
                angular = 0.0

                if not action.startswith("STOPPED"):
                    action = "STOPPED"

            elif node.mode == "MANUAL":

                if manual_command:

                    node.publish_cmd(linear, angular)

                else:

                    # Unknown gesture or hand lost
                    node.publish_cmd(0.0, 0.0)

                    linear = 0.0
                    angular = 0.0

                    if (
                        time.monotonic()
                        - node.last_manual_time
                        > HAND_TIMEOUT
                    ):
                        node.mode = "STOP"
                        action = "STOPPED - HAND LOST"
                    else:
                        action = "WAITING - ROBOT STOPPED"

            # AUTO publishes no continuous gesture commands.
            # twist_mux returns authority to Nav2 after timeout.

            # ===== ON-SCREEN DISPLAY =====

            color = (
                (0, 220, 80)
                if node.mode == "MANUAL"
                else (255, 255, 255)
            )

            cv2.putText(
                frame,
                f"Gesture: {gesture} ({score:.2f})",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"MODE: {node.mode}",
                (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.85,
                (255, 255, 255),
                2
            )

            cv2.putText(
                frame,
                f"ACTION: {action}",
                (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                color,
                2
            )

            cv2.putText(
                frame,
                f"cmd_vel: x={linear:+.2f}  yaw={angular:+.2f}",
                (20, 160),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (255, 255, 255),
                2
            )

            cv2.imshow(
                "NavBot-X Gesture Controller",
                frame
            )

            rclpy.spin_once(
                node, timeout_sec=0.001
            )

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:

        # Send stop command on shutdown
        node.publish_cmd(0.0, 0.0)

        if cap is not None:
            cap.release()

        if recognizer is not None:
            recognizer.close()

        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
