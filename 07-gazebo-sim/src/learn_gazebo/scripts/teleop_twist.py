#!/usr/bin/env python3
"""第 07 课：键盘遥控节点。

读取键盘输入，向 /cmd_vel 发布 geometry_msgs/Twist，遥控差速机器人。

按键:
    i  前进      ,  后退
    j  左转      l  右转
    u  左前      o  右前
    m  左后      .  右后
    k / 空格      停止
    q / Ctrl+C    退出
    z / x         增大 / 减小线速度
    a / s         增大 / 减小角速度

运行:
    ros2 run learn_gazebo teleop_twist.py
"""

import sys
import termios
import tty

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

USAGE = """
-----------------------------------
   u   i   o        z: 加速  x: 减速
   j   k   l        a: 加转角 s: 减转角
   m   ,   .        空格/k: 停止  q: 退出
-----------------------------------
"""

# 按键 -> (线速度方向, 角速度方向)
KEY_MAP = {
    'i': (1, 0), 'j': (0, 1), 'l': (0, -1), ',': (-1, 0),
    'u': (1, 1), 'o': (1, -1), 'm': (-1, 1), '.': (-1, -1),
    'k': (0, 0), ' ': (0, 0),
}


def read_key():
    """从终端读取一个按键（阻塞）。"""
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch


class Teleop(Node):
    def __init__(self):
        super().__init__('teleop_twist')
        self._pub = self.create_publisher(Twist, 'cmd_vel', 10)
        self.linear = 0.3
        self.angular = 0.8

    def publish(self, lin_dir, ang_dir):
        msg = Twist()
        msg.linear.x = float(lin_dir) * self.linear
        msg.angular.z = float(ang_dir) * self.angular
        self._pub.publish(msg)
        self.get_logger().info(
            f'cmd_vel: linear.x={msg.linear.x:.2f}, angular.z={msg.angular.z:.2f}')

    def stop(self):
        self._pub.publish(Twist())


def main(args=None):
    rclpy.init(args=args)
    node = Teleop()
    print(USAGE)
    try:
        while rclpy.ok():
            key = read_key()
            if key in KEY_MAP:
                node.publish(*KEY_MAP[key])
            elif key == 'z':
                node.linear = min(node.linear + 0.05, 1.0)
                print(f'线速度 -> {node.linear:.2f}')
            elif key == 'x':
                node.linear = max(node.linear - 0.05, 0.05)
                print(f'线速度 -> {node.linear:.2f}')
            elif key == 'a':
                node.angular = min(node.angular + 0.1, 2.0)
                print(f'角速度 -> {node.angular:.2f}')
            elif key == 's':
                node.angular = max(node.angular - 0.1, 0.1)
                print(f'角速度 -> {node.angular:.2f}')
            elif key == 'q' or key == '\x03':  # q 或 Ctrl+C
                break
    finally:
        node.stop()
        node.destroy_node()
        rclpy.shutdown()
        print('\n已停止并退出。')


if __name__ == '__main__':
    main()
