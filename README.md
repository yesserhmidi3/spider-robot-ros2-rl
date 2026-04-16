# Spider Robot ROS 2 Control & RL Simulation

![ROS 2](https://img.shields.io/badge/ROS2-Jazzy-blue)
![Gazebo](https://img.shields.io/badge/Gazebo-Harmonic-orange)
![License](https://img.shields.io/badge/License-MIT-green)

This repository tracks the development of a quadruped spider robot simulation built with **ROS 2 Jazzy** and **Gazebo Harmonic**. The project focuses on bridging the gap between mechanical design (SolidWorks) and intelligent locomotion using Reinforcement Learning, documented step-by-step.

## Development Journey

### Step 1: Mechanical Export (SolidWorks to URDF)
The project began by designing the robot in SolidWorks. To ensure realistic physics in Gazebo, I used the SW2URDF exporter plugin to carefully capture the exact mass, collision boundaries, and inertias (including realistic metrics for SG90 servos). 
* *Resource:* I followed this 3-part YouTube tutorial series ([Part 1](https://www.youtube.com/watch?v=Id8zVHrQSlE), [Part 2](https://www.youtube.com/watch?v=SDr6ru8R0qc), [Part 3](https://www.youtube.com/watch?v=wxxRuM_qZtE&t=777s)) for the exportation process.

### Step 2: ROS 2 Control & GUI Validation
Once the URDF was in Gazebo, I configured a hardware abstraction layer using `gz_ros2_control`. I set up the `joint_state_broadcaster` and a `joint_trajectory_controller` for 8-DOF position control. I initially tested the kinematics and URDF limits using the `rqt_joint_trajectory_controller` GUI to ensure the spider could move.

![Step 2 GUI Validation](media/step2.gif)

### Step 3: Validating the Action/Observation Pipeline (Current State)
To prepare for Reinforcement Learning, I needed to guarantee that Python could communicate flawlessly with Gazebo. I built an initial prototype control node (`control.py`) to serve as a stand-in for the future AI agent:
* **Simulating Observations:** It subscribes to `/joint_states` to read the robot's current position.
* **Simulating Actions:** Instead of an AI policy, it takes manual terminal inputs, formats them with zero-velocities and accurate time stamps, and publishes them to the trajectory controller.
* **Result:** The two-way communication bridge is 100% verified. In the upcoming phase, the manual terminal input in `control.py` will be replaced by a Gymnasium-compatible wrapper and a neural network policy.

![Step 3 Terminal Control](media/step3.gif)

## Tech Stack
* **Middleware:** ROS 2 Jazzy Jalisco
* **Simulator:** Gazebo Harmonic (GZ Sim)
* **Language:** Python / C++
* **Tools:** SolidWorks, URDF, RQT

## Project Structure
* `urdf/`: Contains the robot description and physical properties.
* `config/`: YAML files defining the controller parameters and update rates.
* `launch/`: Python scripts to orchestrate the simulation, spawners, and state publishers.
* `meshes/`: STL/DAE files for visual and collision representation.
* `spider/`: Contains the custom Python nodes, including the terminal control interface (`control.py`).

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
4. **Run Terminal Control Node (In a new terminal):**
   ```bash
   source install/setup.bash
   ros2 run spider control_node
   ```

## Roadmap & Next Steps
With the communication pipeline established, the next steps focus on autonomous locomotion:
1. **Phase 1: Environment Wrapping**
   Create a Gymnasium-compatible wrapper for the Gazebo simulation using the verified **control.py** logic for observations and actions.   
2. **Phase 2: Static Stability (Standing)**
    Train a PPO (Proximal Policy Optimization) agent to maintain a stable stance and height.
3. **Phase 3: Locomotion (Gait Generation)**
    Implement reward functions based on forward velocity and energy efficiency to teach the spider to walk.



