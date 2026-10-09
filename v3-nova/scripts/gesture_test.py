import cv2
import mediapipe as mp

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
RunningMode = mp.tasks.vision.RunningMode

from pathlib import Path
MODEL = str(Path(__file__).resolve().parents[1] / "models" / "gesture_recognizer.task")

options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=MODEL),
    running_mode=RunningMode.IMAGE,
    num_hands=1,
)

recognizer = GestureRecognizer.create_from_options(options)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Could not open webcam")

print("Press Q to quit")

while True:
    ok, frame = cap.read()
    if not ok:
        break

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb
    )

    result = recognizer.recognize(mp_image)

    gesture_name = "No hand"
    score = 0.0

    if result.gestures and len(result.gestures[0]) > 0:
        gesture = result.gestures[0][0]
        gesture_name = gesture.category_name
        score = gesture.score

    cv2.putText(
        frame,
        f"{gesture_name}  {score:.2f}",
        (20, 50),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 255),
        2
    )

    cv2.imshow("NavBot-X Gesture Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
recognizer.close()
cv2.destroyAllWindows()
