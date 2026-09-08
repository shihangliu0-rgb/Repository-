"""第 07 课：一键拉起完整仿真。

包含:
    1. robot_state_publisher —— 发布机器人模型与 TF
    2. Gazebo（gz sim）      —— 加载世界并运行物理仿真
    3. ros_gz_sim create     —— 把机器人模型生成（spawn）进世界
    4. ros_gz_bridge         —— 桥接 /clock 与 /scan
    (控制器由 URDF 里的 gz_ros2_control 插件自动加载并激活)

运行:
    ros2 launch learn_gazebo sim.launch.py
    ros2 launch learn_gazebo sim.launch.py rviz:=true     # 顺带打开 RViz 看雷达
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_learn_gazebo = get_package_share_directory('learn_gazebo')
    pkg_learn_description = get_package_share_directory('learn_description')

    # ---------- 启动参数 ----------
    use_sim_time = LaunchConfiguration('use_sim_time')
    world_file = LaunchConfiguration('world')

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time', default_value='true',
        description='使用仿真时钟（仿真里务必为 true）')
    declare_world = DeclareLaunchArgument(
        'world',
        default_value=os.path.join(pkg_learn_gazebo, 'worlds', 'simple_world.sdf'),
        description='世界文件 (.sdf) 的完整路径')
    declare_rviz = DeclareLaunchArgument(
        'rviz', default_value='false', description='是否打开 RViz')

    # ---------- 1. 机器人模型 ----------
    xacro_file = os.path.join(pkg_learn_description, 'urdf', 'robot.urdf.xacro')
    robot_description = Command(['xacro ', xacro_file])

    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': use_sim_time,
        }],
        output='screen',
    )

    # ---------- 2. Gazebo 世界 ----------
    # gz_sim.launch.py 会把 gz_args 拼到 `gz sim` 命令后面
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'),
                         'launch', 'gz_sim.launch.py')),
        launch_arguments={'gz_args': ['-r -v 1 ', world_file]}.items(),
    )

    # ---------- 3. 生成机器人 ----------
    # 从 /robot_description 话题读取模型，放到 (-2, 0) 处
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'learning_bot',
            '-x', '-2.0',
            '-y', '0.0',
            '-z', '0.15',
        ],
        output='screen',
    )

    # ---------- 4. 桥接 ----------
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': os.path.join(pkg_learn_gazebo, 'config', 'bridge.yaml'),
            'use_sim_time': use_sim_time,
        }],
        output='screen',
    )

    # ---------- 可选：RViz ----------
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        arguments=['-d', os.path.join(pkg_learn_gazebo, 'rviz', 'sim.rviz')],
        parameters=[{'use_sim_time': use_sim_time}],
        condition=IfCondition(LaunchConfiguration('rviz')),
        output='screen',
    )

    return LaunchDescription([
        declare_use_sim_time, declare_world, declare_rviz,
        robot_state_publisher, gz_sim, spawn_robot, bridge, rviz,
    ])
