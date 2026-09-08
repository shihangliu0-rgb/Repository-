"""第 09 课：一键启动「仿真 + SLAM 建图 + RViz」。

组成:
    1. learn_gazebo/sim.launch.py  —— Gazebo 世界 + 机器人 + 桥接（第 07 课）
    2. slam_toolbox (online_async) —— 实时建图，发布 map->odom TF 与 /map
    3. rviz2                        —— 显示 /map 与 /scan

运行:
    ros2 launch slam_demo slam.launch.py
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    pkg_slam_demo = get_package_share_directory('slam_demo')
    pkg_learn_gazebo = get_package_share_directory('learn_gazebo')
    pkg_slam_toolbox = get_package_share_directory('slam_toolbox')

    slam_params = os.path.join(pkg_slam_demo, 'config', 'mapper_params_online_async.yaml')
    rviz_config = os.path.join(pkg_slam_demo, 'rviz', 'slam.rviz')

    # 1) 仿真（机器人 + 雷达 + 桥接）
    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_learn_gazebo, 'launch', 'sim.launch.py')),
        launch_arguments={'use_sim_time': 'true'}.items(),
    )

    # 2) slam_toolbox（复用官方 launch，传入我们的参数文件）
    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_slam_toolbox, 'launch', 'online_async_launch.py')),
        launch_arguments={
            'use_sim_time': 'true',
            'params_file': slam_params,
        }.items(),
    )

    # 3) RViz：地图 + 激光 + 机器人模型 + TF
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}],
        output='screen',
    )

    return LaunchDescription([sim, slam, rviz])
