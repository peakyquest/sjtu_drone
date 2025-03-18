#!/usr/bin/env python3

import os
import yaml

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource

import xacro


def generate_launch_description():
    # Define launch arguments
    use_sim_time = LaunchConfiguration("use_sim_time", default="true")

    # New launch arguments for specifying spawn position
    x_pos = LaunchConfiguration("x", default="0.0")
    y_pos = LaunchConfiguration("y", default="0.0")
    z_pos = LaunchConfiguration("z", default="1.0")

    xacro_file_name = "sjtu_drone.urdf.xacro"
    
    xacro_file = os.path.join(
        get_package_share_directory("sjtu_drone_description"),
        "urdf", xacro_file_name
    )
    
    yaml_file_path = os.path.join(
        get_package_share_directory('sjtu_drone_bringup'),
        'config', 'robot_2.yaml'
    )   
    
    # Process xacro file with parameters
    robot_description_config = xacro.process_file(xacro_file, mappings={"params_path": yaml_file_path})
    robot_desc = robot_description_config.toxml()

    # Get namespace from YAML
    model_ns = "drone"
    with open(yaml_file_path, 'r') as f:
        yaml_dict = yaml.load(f, Loader=yaml.FullLoader)
        model_ns = yaml_dict["namespace"]  # Assign from YAML
    print("Namespace:", model_ns)


    return LaunchDescription([
        # Declare launch arguments
        DeclareLaunchArgument("x", default_value="5.0", description="Initial X position"), # Change the value of x y and z
        DeclareLaunchArgument("y", default_value="0.0", description="Initial Y position"),
        DeclareLaunchArgument("z", default_value="1.0", description="Initial Z position"),

        # Robot State Publisher
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            namespace=model_ns,
            output="screen",
            parameters=[{"use_sim_time": use_sim_time, "robot_description": robot_desc, "frame_prefix": model_ns + "/"}],
            arguments=[robot_desc]
        ),

        # Joint State Publisher
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            name='joint_state_publisher',
            namespace=model_ns,
            output='screen',
        ),

        # Spawn Drone at Specified Position
        Node(
            package="sjtu_drone_bringup",
            executable="spawn_robot",
            arguments=[robot_desc, model_ns, x_pos, y_pos, z_pos],
            output="screen"
        ),

        # Static Transform from World to Odom
        Node(
            package="tf2_ros",
            executable="static_transform_publisher",
            arguments=[x_pos, y_pos, z_pos, "0", "0", "0", "world", f"{model_ns}/odom"],
            output="screen"
        ),
    ])
