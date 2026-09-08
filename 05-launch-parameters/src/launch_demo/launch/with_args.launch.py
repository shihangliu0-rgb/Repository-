"""第 05 课 · Launch ②：启动参数（命令行传值）。

运行:
    ros2 launch launch_demo with_args.launch.py
    ros2 launch launch_demo with_args.launch.py message:="自定义内容" frequency:=3.0
    ros2 launch launch_demo with_args.launch.py --show-args
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # 1) 声明启动参数（名字 + 默认值 + 说明）
    message_arg = DeclareLaunchArgument(
        'message',
        default_value='Hello from launch argument',
        description='talker 发布的文本内容',
    )
    freq_arg = DeclareLaunchArgument(
        'frequency',
        default_value='2.0',
        description='发布频率（Hz）',
    )

    # 2) 用 LaunchConfiguration 读取参数值，塞进节点参数
    #    注意：此刻只是"占位"，真正取值发生在启动时刻。
    talker = Node(
        package='launch_demo',
        executable='talker',
        name='talker',
        output='screen',
        parameters=[{
            'message': LaunchConfiguration('message'),
            'publish_frequency': LaunchConfiguration('frequency'),
        }],
    )

    listener = Node(
        package='launch_demo',
        executable='listener',
        name='listener',
        output='screen',
    )

    return LaunchDescription([message_arg, freq_arg, talker, listener])
