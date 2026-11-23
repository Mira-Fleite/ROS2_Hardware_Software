import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('my_py_pkg')
    params_file = os.path.join(pkg_share, 'config', 'params.yaml')

    return LaunchDescription([
        Node(
            package='my_py_pkg',
            executable='control_node_params',
            name='control_node_params',
            parameters=[params_file],
            output='screen',
        ),
        Node(
            package='my_py_pkg',
            executable='actuator_node_params',
            name='actuator_node_params',
            parameters=[params_file],
            output='screen',
        ),
    ])