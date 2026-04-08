from __future__ import annotations

import cv2
import mediapipe as mp


class GestureInput:
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            raise RuntimeError("Could not open webcam.")

        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.last_command = "STOP"

    def close(self):
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()

    def _count_extended_fingers(self, landmarks):
        tips = {"index": 8, "middle": 12, "ring": 16, "pinky": 20}
        pips = {"index": 6, "middle": 10, "ring": 14, "pinky": 18}

        count = 0
        for name in tips:
            if landmarks[tips[name]].y < landmarks[pips[name]].y:
                count += 1

        if abs(landmarks[4].x - landmarks[3].x) > 0.04:
            count += 1

        return count

    def _classify_command(self, landmarks):
        wrist = landmarks[0]
        extended = self._count_extended_fingers(landmarks)

        if extended >= 4:
            return "STOP"

        if extended == 0:
            return "BACKWARD"

        index_up = landmarks[8].y < landmarks[6].y
        middle_down = landmarks[12].y > landmarks[10].y
        ring_down = landmarks[16].y > landmarks[14].y
        pinky_down = landmarks[20].y > landmarks[18].y

        if index_up and middle_down and ring_down and pinky_down:
            return "FORWARD"

        if wrist.x < 0.35:
            return "LEFT"
        if wrist.x > 0.65:
            return "RIGHT"

        return "STOP"

    def get_command(self, show_window: bool = True):
        ok, frame = self.cap.read()
        if not ok:
            return "STOP"

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb)

        command = "STOP"

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            landmarks = hand_landmarks.landmark
            command = self._classify_command(landmarks)

            if show_window:
                self.mp_draw.draw_landmarks(
                    frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                )

        self.last_command = command

        if show_window:
            cv2.putText(
                frame,
                f"Gesture Command: {command}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (255, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.imshow("NavBot-X Gesture Input", frame)
            cv2.waitKey(1)

        return command