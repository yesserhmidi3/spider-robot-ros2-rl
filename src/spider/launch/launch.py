import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():
    package_name = 'spider'
    urdf_file = 'Spider_URDF.urdf'

    pkg_path = get_package_share_directory(package_name)
    urdf_path = os.path.join(pkg_path, 'urdf', urdf_file)
    config_path = os.path.join(pkg_path, 'config', 'controllers.yaml') # added config path to controllers.yaml to define the joints


    # CRITICAL: This allows Gazebo to find your meshes without absolute paths
    os.environ["GZ_SIM_RESOURCE_PATH"] = os.path.join(pkg_path, "..")

    with open(urdf_path, 'r') as infp:
        robot_desc = infp.read()

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        output='screen',
        parameters=[{'robot_description': robot_desc, 'use_sim_time': True}]
    )

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')]),
        launch_arguments={'gz_args': '-r empty.sdf'}.items(),
    )

    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'spider_robot',
            '-topic', 'robot_description',
            '-x', '0', '-y', '0', '-z', '0.2', # Spawning slightly lower so it doesn't bounce
            # STANDING POSE ARGUMENTS
            '-J', 'L1_J2', '0.4', '-J', 'L1_J3', '0.6',
            '-J', 'L2_J2', '0.4', '-J', 'L2_J3', '0.6',
            '-J', 'L3_J2', '0.4', '-J', 'L3_J3', '0.6',
            '-J', 'L4_J2', '0.4', '-J', 'L4_J3', '0.6',
        ],
        output='screen'
    )

    # Controller manager node // new after .yaml added
    controller_manager = Node(
        package='controller_manager',
        executable='ros2_control_node',
        parameters=[config_path],
        output='screen',
    )

    

    # Spawn joint state broadcaster (broadcasts joint states from Gazebo)
    spawn_jsb = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster'],
        output='screen',
    )

    # Spawn joint trajectory controller
    spawn_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_trajectory_controller'],
        output='screen',
    )


    # RQT GUI for joint control (alternative to joint_state_publisher_gui)
    '''rqt_joint_trajectory_controller = Node(
        package='rqt_joint_trajectory_controller',
        executable='rqt_joint_trajectory_controller',
        name='rqt_joint_trajectory_controller',
    )'''#commented this to used control_node intead of rqt gui interface to control joints

    #IMU bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/imu@sensor_msgs/msg/Imu@gz.msgs.IMU'
        ],
        output='screen'
    ) 

    return LaunchDescription([
        robot_state_publisher,
        gazebo,
        spawn_robot,
        controller_manager,
        spawn_jsb,  # Broadcast joint states
        spawn_controller,  # Joint trajectory controller
        bridge, #IMU bridge
        #joint_state_publisher_gui,  # GUI with sliders
        #rqt_joint_trajectory_controller # RQT GUI for joint control
    ])