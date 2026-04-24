import rclpy
from rclpy.node import Node
import threading #because ros2 node and ppo algorithm have to work continuously , so we use threading so each one can have their own thread
import time
import numpy as np
import subprocess # Added to send terminal commands from Python
import math       # Added for quaternion math

# Gymnasium imports
import gymnasium as gym
from gymnasium import spaces

# ROS 2 message imports
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint 
from sensor_msgs.msg import Imu, JointState


def euler_from_quaternion(x, y, z, w):    #Convert IMU quaternion to Euler angles (Roll, Pitch, Yaw)
    t0 = +2.0 * (w * x + y * z)
    t1 = +1.0 - 2.0 * (x * x + y * y)
    roll_x = math.atan2(t0, t1)
    
    t2 = +2.0 * (w * y - z * x)
    t2 = +1.0 if t2 > +1.0 else t2
    t2 = -1.0 if t2 < -1.0 else t2
    pitch_y = math.asin(t2)
    
    t3 = +2.0 * (w * z + x * y)
    t4 = +1.0 - 2.0 * (y * y + z * z)
    yaw_z = math.atan2(t3, t4)
    
    return roll_x, pitch_y, yaw_z


# 1. THE ROS 2 DATA HANDLER (Runs in a separate thread)
class SpiderROSNode(Node): # Same as control.py just added the IMU for body orientation feedback
    def __init__(self):
        super().__init__('spider_rl_interface')

        self.joint_pub = self.create_publisher(JointTrajectory, '/joint_trajectory_controller/joint_trajectory', 10)
        self.joint_sub = self.create_subscription(JointState, '/joint_states', self.joint_callback, 10)
        self.imu_sub = self.create_subscription(Imu, '/imu', self.imu_callback, 10)

        self.joint_names = [
            'L1_J1', 'L1_J2', 'L1_J3', 
            'L2_J1', 'L2_J2', 'L2_J3', 
            'L3_J1', 'L3_J2', 'L3_J3',
            'L4_J1', 'L4_J2', 'L4_J3'
        ]        
        
        # Latest sensor data
        self.current_joint_positions = np.zeros(12)
        self.current_pitch = 0.0 
        self.current_roll = 0.0

    def joint_callback(self, msg):
        for i, name in enumerate(self.joint_names):
            if name in msg.name:
                idx = msg.name.index(name)
                self.current_joint_positions[i] = msg.position[idx]

    def imu_callback(self, msg):
        q = msg.orientation
        roll, pitch, _ = euler_from_quaternion(q.x, q.y, q.z, q.w)
        self.current_roll = roll
        self.current_pitch = pitch 

    def send_action(self, action_array): #Formats RL numpy array into a ROS 2 Trajectory message
        msg = JointTrajectory()
        msg.joint_names = self.joint_names

        point = JointTrajectoryPoint()
        point.positions = action_array.tolist()
        
        # RL step time 
        point.time_from_start.sec = 0
        point.time_from_start.nanosec = 100000000 
        
        msg.points.append(point)
        self.joint_pub.publish(msg)

# 2. THE GYMNASIUM ENVIRONMENT
class SpiderEnv(gym.Env):
    def __init__(self):
        super(SpiderEnv, self).__init__()

        #1. Start ROS 2 Node in a separate Thread 
        rclpy.init()
        self.node = SpiderROSNode()
        self.ros_thread = threading.Thread(target=rclpy.spin, args=(self.node,), daemon=True)
        self.ros_thread.start()

        #  2. Define the Spaces for the AI 
        self.action_space = spaces.Box(low=-1.5, high=1.5, shape=(12,), dtype=np.float32)
        
        # Observation: 12 joint angles + 2 body angles (pitch, roll) = 14 total numbers
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(14,), dtype=np.float32)

        # 3. Define the "Standing" Home Pose
        # J1=0.0, J2=0.4, J3=0.6 for all 4 legs
        self.home_pose = np.array([
            0.0, 0.4, 0.6, 
            0.0, 0.4, 0.6, 
            0.0, 0.4, 0.6, 
            0.0, 0.4, 0.6
        ], dtype=np.float32)

    def _get_obs(self):#Gathers the latest data from the ROS thread to feed to the RL
        joints = self.node.current_joint_positions
        orientation = np.array([self.node.current_pitch, self.node.current_roll])
        return np.concatenate((joints, orientation)).astype(np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed) #resets joints and robot 
        
        # Step 1: Tell the joints to move to the standing position
        self.node.send_action(self.home_pose)
        time.sleep(0.2) # Give joints time to move
        
        # Step 2: Teleport the robot back to the center in Gazebo using the terminal
        reset_cmd = ( #this is gazebo reset cmd comand 
            "gz service -s /world/empty/set_pose "
            "--reqtype gz.msgs.Pose "
            "--reptype gz.msgs.Boolean "
            "--req 'name: \"spider_robot\", position: {x: 0, y: 0, z: 0.2}, orientation: {x: 0, y: 0, z: 0, w: 1}'"
        )
        subprocess.run(reset_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) # we used subprocess to open new terminal and do gz service immediatly without waiting for ros2

        # Step 3: Wait for Gazebo physics to settle (robot dropping to the floor)
        time.sleep(0.5) 
        
        obs = self._get_obs()
        return obs, {}

    def step(self, action):#The core loop (reward system)
        # 1. Send the RL's chosen action to Gazebo
        self.node.send_action(action)
        
        # 2. Wait a fraction of a second for physics to happen
        time.sleep(0.1) 
        
        # 3. Read new states
        obs = self._get_obs()
        
        # 4. Did the robot fall over?
        terminated = False
        # If pitched forward/backward OR rolled side-to-side more than ~45 degrees (0.8 rad)
        if abs(self.node.current_pitch) > 0.8 or abs(self.node.current_roll) > 0.8: 
            terminated = True
            
        # 5. Calculate how good that action was
        reward = 0.0
        if not terminated:
            reward = 1.0 
            
        truncated = False 
        info = {}

        return obs, reward, terminated, truncated, info

    def close(self):
        rclpy.shutdown()
        self.ros_thread.join()