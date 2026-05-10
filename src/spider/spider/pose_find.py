import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from geometry_msgs.msg import Pose
import math

class SmartCalibrator(Node):
    def __init__(self):
        super().__init__('smart_calibrator')
        self.pub = self.create_publisher(JointTrajectory, '/joint_trajectory_controller/joint_trajectory', 10)
        self.sub = self.create_subscription(Pose, '/model/spider_robot/pose', self.pose_callback, 10)

        # Order: L1_J2, L1_J3, L2_J2, L2_J3, L3_J2, L3_J3, L4_J2, L4_J3
        self.joint_names = ['L1_J2', 'L1_J3', 'L2_J2', 'L2_J3', 'L3_J2', 'L3_J3', 'L4_J2', 'L4_J3']
        
        # Start with everything at 0.0
        self.current_offsets = [0.0] * 8
        
        self.current_roll = 0.0
        self.current_pitch = 0.0
        self.current_z = 0.0

        # TARGETS: We want 0 roll, 0 pitch, and a standing height (e.g., 0.05 meters)
        self.target_z = 0.05 

        # How aggressively it corrects (Tune these if it vibrates or moves too slow)
        self.learning_rate_tilt = 0.1 
        self.learning_rate_height = 0.5 

        self.timer = self.create_timer(1.0, self.optimization_step) # Run every 1 second

    def pose_callback(self, msg):
        q = msg.orientation
        sinr_cosp = 2 * (q.w * q.x + q.y * q.z)
        cosr_cosp = 1 - 2 * (q.x * q.x + q.y * q.y)
        self.current_roll = math.atan2(sinr_cosp, cosr_cosp)
        
        sinp = 2 * (q.w * q.y - q.z * q.x)
        self.current_pitch = math.asin(sinp)
        
        # Get the height of the main body
        self.current_z = msg.position.z

    def optimization_step(self):
        # 1. Calculate errors
        roll_error = 0.0 - self.current_roll
        pitch_error = 0.0 - self.current_pitch
        z_error = self.target_z - self.current_z

        self.get_logger().info(f"Errors -> Roll: {roll_error:.3f} | Pitch: {pitch_error:.3f} | Z: {z_error:.3f}")

        # 2. SMART ADJUSTMENTS (Adjusting J3 joints to push legs up/down)
        # Assuming +J3 pushes the leg down (you might need to invert the signs based on your axes)
        
        # Front Right (L1)
        self.current_offsets[1] += (z_error * self.learning_rate_height) + (pitch_error * self.learning_rate_tilt) - (roll_error * self.learning_rate_tilt)
        # Front Left (L2)
        self.current_offsets[3] += (z_error * self.learning_rate_height) + (pitch_error * self.learning_rate_tilt) + (roll_error * self.learning_rate_tilt)
        # Back Right (L3)
        self.current_offsets[5] += (z_error * self.learning_rate_height) - (pitch_error * self.learning_rate_tilt) - (roll_error * self.learning_rate_tilt)
        # Back Left (L4)
        self.current_offsets[7] += (z_error * self.learning_rate_height) - (pitch_error * self.learning_rate_tilt) + (roll_error * self.learning_rate_tilt)

        self.get_logger().info(f"New Offsets: {[round(x, 3) for x in self.current_offsets]}")

        # 3. Publish the new offsets
        msg = JointTrajectory()
        msg.joint_names = self.joint_names
        point = JointTrajectoryPoint()
        point.positions = self.current_offsets
        point.time_from_start.sec = 1
        msg.points.append(point)
        self.pub.publish(msg)

def main():
    rclpy.init()
    node = SmartCalibrator()
    rclpy.spin(node)

if __name__ == '__main__':
    main()