from pathlib import Path
from navbot_x_isaac_lab.demo.gesture_input import GestureInput

OUT = Path("/tmp/navbot_x_gesture_command.txt")

gi = GestureInput()
print("Gesture writer running. Ctrl+C to stop.")

try:
    while True:
        cmd = gi.get_command(show_window=True)
        OUT.write_text(cmd)
        print(f"\r{cmd}", end="")
except KeyboardInterrupt:
    pass
finally:
    OUT.write_text("STOP")
    gi.close()
    print("\nStopped.")