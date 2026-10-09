# NavBot-X V3 — Nova Carter, ROS 2, SLAM, Nav2 and gesture control

This folder contains the **Isaac Sim 6.0.1** implementation of NavBot-X, an autonomous inspection robot in a simulated warehouse. It builds on earlier Gazebo and Isaac Lab versions with custom-trained PPO navigation, but **V3's demonstrated goal navigation uses Nav2 rather than an RL policy**.

## Verified features from development machine

- Isaac Sim's Nova Carter robot in a warehouse scene (`scenes/navbot_V3.usd`).
- ROS 2 Jazzy topics for drive commands, 3D LiDAR, odometry and simulation clock.
- Manual driving with `geometry_msgs/msg/Twist` on `/cmd_vel`.
- LiDAR PointCloud2 to 2D LaserScan conversion; SLAM Toolbox occupancy map, saved in `maps/`.
- AMCL map localization and Nav2 RViz goal navigation; a goal was reached in simulation.
- MediaPipe recognition of hand gestures and `twist_mux` command switching.

**Limits:** This setup has not yet been tested from a fresh clone on a second computer. Isaac's scene uses external NVIDIA-hosted assets, and the combined Nav2/gesture workflow may require timing and lifecycle checks after startup.

## Requirements

- Ubuntu 24.04 on an NVIDIA GPU computer compatible with Isaac Sim 6.0.1.
- NVIDIA Isaac Sim **6.0.1** (`isaac-sim.sh` installed locally).
- ROS 2 **Jazzy**, with Fast DDS available.
- An internet connection for NVIDIA-hosted robot/warehouse USD asset references, unless already cached.
- Webcam for gesture control.

Install ROS 2 Jazzy first, then install these packages:

```bash
sudo apt update
sudo apt install -y \
  ros-jazzy-navigation2 \
  ros-jazzy-nav2-bringup \
  ros-jazzy-slam-toolbox \
  ros-jazzy-rviz2 \
  ros-jazzy-pointcloud-to-laserscan \
  ros-jazzy-twist-mux \
  python3-venv curl
```

For the gesture environment, use a virtual environment that can see system ROS 2 Python packages:

```bash
python3 -m venv --system-site-packages ~/navbot_gesture_env
source ~/navbot_gesture_env/bin/activate
python -m pip install 'numpy<2' 'opencv-contrib-python==4.10.0.84' 'mediapipe==1.1.0'
# From the repo root:
bash v3-nova/setup/download_gesture_model.sh
```

Dependency versions above reflect the working development environment, but compatibility should be verified on the destination machine. Check that `rclpy`, `mediapipe`, `cv2` can all import in your configured gesture environment.

## Scene launch

From a ROS 2 Jazzy terminal, set the ROS middleware implementation and launch Isaac Sim using your local installation path:

```bash
source /opt/ros/jazzy/setup.bash
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
~/isaacsim-6.0.1/isaac-sim.sh
```

Open `v3-nova/scenes/navbot_V3.usd` and **Play**. Ensure ROS 2 Bridge is enabled and the saved `/clock` publisher is active.

**USD asset references:** The file references NVIDIA's hosted `Nova_Carter_ROS.usd` and `warehouse_20x20_envi.usd`. The small scene file is not a self-contained copy of those assets. Network access may be required.

Verify communication:

```bash
source /opt/ros/jazzy/setup.bash
ros2 topic list -t
ros2 topic echo /clock --once
ros2 topic echo /chassis/odom --once --field header
ros2 topic info /front_3d_lidar/lidar_points
```

## LiDAR: PointCloud2 to `/scan`

Keep the simulator playing, then open a new terminal:

```bash
source /opt/ros/jazzy/setup.bash
ros2 run pointcloud_to_laserscan pointcloud_to_laserscan_node \
  --ros-args \
  -r cloud_in:=/front_3d_lidar/lidar_points \
  -r scan:=/scan \
  -p min_height:=-0.5 \
  -p max_height:=0.5 \
  -p range_min:=0.3 \
  -p range_max:=20.0
```

This converter is subscription-driven. Subscribe to `/scan` in RViz or from a terminal to trigger processing. The saved occupancy grid is `maps/warehouse_map.yaml` and `maps/warehouse_map.pgm`.

## Autonomous navigation (Nav2)

From the **repository root**:

```bash
source /opt/ros/jazzy/setup.bash
ros2 launch nav2_bringup bringup_launch.py \
  map:="$PWD/v3-nova/maps/warehouse_map.yaml" \
  params_file:="$PWD/v3-nova/config/navbot_nav2.yaml" \
  use_sim_time:=true autostart:=true use_composition:=False
```

In a separate terminal:

```bash
source /opt/ros/jazzy/setup.bash
rviz2 -d "$(ros2 pkg prefix nav2_bringup)/share/nav2_bringup/rviz/nav2_default_view.rviz"
```

In RViz, select **2D Pose Estimate** to initialize AMCL, then select a **Nav2 Goal**. A valid `map → odom → base_link` TF chain and active Nav2 lifecycle nodes are required. If Nav2 does not navigate, check `/clock`, `/scan`, TF and server activation before sending another goal.

## Manual drive test

For a basic drive test **before enabling `twist_mux`**, publish to `/cmd_vel`:

```bash
source /opt/ros/jazzy/setup.bash
ros2 topic pub -r 10 /cmd_vel geometry_msgs/msg/Twist \
  '{linear: {x: 0.15}, angular: {z: 0.0}}'
```

Stop with Ctrl+C, then publish a zero command. **Do not publish directly to `/cmd_vel` while the mux is acting as the command owner**, to avoid competing publishers.

## Gesture control and `twist_mux`

The working architecture uses `/cmd_vel_auto` from the Nav2 collision-monitor output and `/cmd_vel_gesture` from MediaPipe. `twist_mux` selects which command reaches Nova Carter via `/cmd_vel`, giving gesture commands higher priority.

Start the mux from the **repository root**:

```bash
source /opt/ros/jazzy/setup.bash
ros2 run twist_mux twist_mux \
  --ros-args \
  --params-file "$PWD/v3-nova/config/navbot_twist_mux.yaml" \
  -r cmd_vel_out:=/cmd_vel
```

Then run gesture recognition in a separate terminal:

```bash
source /opt/ros/jazzy/setup.bash
source ~/navbot_gesture_env/bin/activate
python v3-nova/scripts/navbot_gesture_control.py
```

| Gesture | Command |
|---|---|
| Pointing Up (center) | Forward |
| Pointing Up (hand left/right) | Turn left/right |
| Thumb Down | Reverse (negative `linear.x`) |
| Open Palm / Closed Fist | STOP |
| Victory | AUTO: stop publishing higher-priority gesture commands and allow Nav2 again |

The script stops manual motion on lost or unrecognized hand input. `twist_mux` timeout and priority values are in `config/navbot_twist_mux.yaml`.

**Before using gesture overrides, verify** that Nav2 is actually publishing to `/cmd_vel_auto` (rather than bypassing the mux) and that the camera-controlled publisher uses `/cmd_vel_gesture`.

## File structure

```text
v3-nova/
  scenes/navbot_V3.usd
  config/navbot_nav2.yaml
  config/navbot_twist_mux.yaml
  maps/warehouse_map.yaml
  maps/warehouse_map.pgm
  scripts/navbot_gesture_control.py
  scripts/gesture_test.py
  scripts/navbot_wasd.py
  setup/download_gesture_model.sh
  models/gesture_recognizer.task  # downloaded locally, not tracked
```

## Reproduction checklist

- [ ] Scene opens and resolves robot/warehouse assets.
- [ ] `/clock`, `/chassis/odom`, and LiDAR topics are active.
- [ ] `/scan` publishes on subscription.
- [ ] The saved warehouse map loads correctly.
- [ ] AMCL produces localization after RViz initial pose.
- [ ] Nav2 plans a path and reaches a selected goal.
- [ ] Gesture controller recognizes movement/STOP/AUTO commands.
- [ ] `twist_mux` routes the intended source to `/cmd_vel`.

## Planned improvements

- Automate and validate fresh-machine setup.
- Validate gesture override and Nav2 resume as one complete demonstration.
- Investigate integrating a **custom-trained** RL navigation policy with V3.
- Future physical inspection-robot testing.
