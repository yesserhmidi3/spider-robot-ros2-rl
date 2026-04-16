import rclpy
from rclpy.node import Node
import threading #for handling joint state updates in a separate thread 
# because normal input blocks rclpy.spin() and prevents callbacks from being processed
#message type for joint trajectory commands
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint 
#messge type for joint state feedback
from sensor_msgs.msg import JointState

class Joint_Control(Node):
    def __init__(self):
        super().__init__('joint_controller')


        # 1.Publish joint trajectory commands to topic /joint_trajectory_controller/joint_trajectory 
        self.pub = self.create_publisher(
            JointTrajectory, 
            '/joint_trajectory_controller/joint_trajectory', 
            10
        )
        
        # 2. subscribe to joint states from topic /joint_states
        self.sub = self.create_subscription(
            JointState, 
            '/joint_states', 
            self.joint_state_callback, 
            10
        )

        self.joint_names = [
                    'L1_J2', 'L1_J3', 'L2_J2', 'L2_J3', 
                    'L3_J2', 'L3_J3', 'L4_J2', 'L4_J3'
                ]        
        
        self.current_positions = []


        # Start a separate thread to handle keyboard input without blocking the main ROS loop
        self.input_thread = threading.Thread(target=self.keyboard_input_loop) # new thread (like new core in the CPU) that will run seperatly from the main thread that runs rclpy.spin() and processes ROS callbacks to not bloc it 
        self.input_thread.daemon = True #when I ctrcl+c kill it with the main loop 
        self.input_thread.start() #begin using this thread

    def joint_state_callback(self, msg):
        #stores the current joint positions from the /joint_states topic
        self.current_positions = msg.position
        #when we'll implement RL , this will be the observation of the environment that the agent will use to learn and make decisions

    def keyboard_input_loop(self):
        while rclpy.ok():
            print(f"\nCurrent robot state: {self.current_positions}")
            key = input(f"Enter joint commands (format: L1_J2 L1_J3 L2_J2 L2_J3 L3_J2 L3_J3 L4_J2 L4_J3):\n>")

            try:
                joints = list(map(float, key.split()))
                if len(joints) != 8:
                    self.get_logger().error("!=8 joint error") 
                    continue

                self.publish_trajectory(joints)
            
            except ValueError:
                self.get_logger().error("Invalid input. Please enter 8 numeric values separated by spaces.")

            
    def publish_trajectory(self, target_positions):
        msg = JointTrajectory()
        msg.joint_names = self.joint_names

        #trajetory point : 
        point = JointTrajectoryPoint()
        point.positions = target_positions

        #stop at the target position (no velocity)
        point.velocities = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] # without this the robot didn't move for me
        #the joint_trajectory_controller needs both position and velocity to execute the command (spline equation) 
        
        #how long to reach the target 
        point.time_from_start.sec = 1 #1 second to reach the target
        point.time_from_start.nanosec = 0 
        msg.points.append(point)

        self.pub.publish(msg)
        self.get_logger().info(f"Published joint trajectory command: {target_positions}")



def main():
    rclpy.init()
    node = Joint_Control()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()