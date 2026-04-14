# Spider Robot ROS 2 Control & RL Simulation

![ROS 2](https://img.shields.io/badge/ROS2-Jazzy-blue)
![Gazebo](https://img.shields.io/badge/Gazebo-Harmonic-orange)
![License](https://img.shields.io/badge/License-MIT-green)

This repository contains the development of a quadruped spider robot simulation built with **ROS 2 Jazzy** and **Gazebo Harmonic**. The project focuses on bridging the gap between mechanical design (SolidWorks) and intelligent locomotion using Reinforcement Learning.

## Current Status: Control Integration
The project has successfully transitioned from a static URDF model to a fully controllable simulation. 

### Key Achievements:
* **Mechanical Pipeline:** Exported complex geometry from SolidWorks to URDF with proper inertial and collision properties.
* **ROS 2 Control Implementation:** Configured a hardware abstraction layer using `gz_ros2_control`.
* **Active Controllers:** Integrated `joint_state_broadcaster` for real-time telemetry and `joint_trajectory_controller` for 8-DOF position control.
* **Manual Validation:** Verified joint kinematics using `rqt_joint_trajectory_controller`.

## Tech Stack
* **Middleware:** ROS 2 Jazzy Jalisco
* **Simulator:** Gazebo Harmonic (GZ Sim)
* **Language:** Python / C++
* **Tools:** SolidWorks, URDF, RQT, LaTeX (for documentation)

## Project Structure
* `urdf/`: Contains the robot description and physical properties.
* `config/`: YAML files defining the controller parameters and update rates.
* `launch/`: Python scripts to orchestrate the simulation, spawners, and state publishers.
* `meshes/`: STL/DAE files for visual and collision representation.

## Installation & Usage
1. **Clone the repo:**
   ```bash
   cd ~/ros2_ws/src
   git clone git@github.com:yesserhmidi3/spider-robot-ros2-rl.git
   ```
2. **Install Dependencies:**
   ```bash
  sudo apt install ros-jazzy-ros2-control ros-jazzy-ros2-controllers ros-jazzy-gz-ros2-control
   ```
3. **Build & Launch:**
   ```bash
  colcon build --packages-select spider
  source install/setup.bash
  ros2 launch spider launch.py
   ```
## Roadmap & Next Steps
The ultimate goal of this project is to achieve autonomous locomotion via Reinforcement Learning.
1. **Phase 1: Environment Wrapping**
    Create a Gymnasium-compatible wrapper for the Gazebo simulation.
2. **Phase 2: Static Stability (Standing)**
    Train a PPO (Proximal Policy Optimization) agent to maintain a stable stance and height.
3. **Phase 3: Locomotion (Gait Generation)**
    Implement reward functions based on forward velocity and energy efficiency to teach the spider to walk.



