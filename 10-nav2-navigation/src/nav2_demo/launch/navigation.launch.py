"""第 10 课：一键启动「仿真 + 地图 + Nav2 导航 + RViz」。

组成:
    1. learn_gazebo/sim.launch.py     —— Gazebo 世界 + 机器人（第 07 课）
    2. nav2_bringup/bringup_launch.py —— map_server + AMCL + Nav2 全部服务器 + RViz

运行:
    ros2 launch nav2_demo navigation.launch.py

参数:
    map:=<地图yaml路径>   换用你自己建的地图（第 09 课保存的）
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, SetParameter


def generate_launch_description():
    pkg_nav2_demo = get_package_share_directory('nav2_demo')
    pkg_learn_gazebo = get_package_share_directory('learn_gazebo')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')

    default_map = os.path.join(pkg_nav2_demo, 'maps', 'learn_map.yaml')
    params_file = os.path.join(pkg_nav2_demo, 'config', 'nav2_params.yaml')

    declare_map = DeclareLaunchArgument(
        'map', default_value=default_map,
        description='地图 YAML 文件路径')

    # 1) 仿真：机器人生于 (-2, 0)，与 AMCL 初始位姿一致
    sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_learn_gazebo, 'launch', 'sim.launch.py')),
        launch_arguments={'use_sim_time': 'true'}.items(),
    )

    # 2) Nav2 完整栈（map_server + AMCL + planner/controller/behavior 等）
    #    注意：bringup_launch.py 自身不启动 RViz，下面单独起。
    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'bringup_launch.py')),
        launch_arguments={
            'map': LaunchConfiguration('map'),
            'params_file': params_file,
            'use_sim_time': 'true',
            'autostart': 'true',
        }.items(),
    )

    # 3) RViz：使用 nav2_bringup 自带的导航视图（含 2D Pose Estimate / Nav2 Goal 工具）
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(pkg_nav2_bringup, 'rviz', 'nav2_default_view.rviz')],
        parameters=[{'use_sim_time': True}],
        output='screen',
    )

    return LaunchDescription([
        declare_map,
        SetParameter(name='use_sim_time', value=True),
        sim,
        nav2,
        rviz,
    ])
