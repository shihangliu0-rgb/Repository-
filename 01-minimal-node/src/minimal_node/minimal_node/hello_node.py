"""第 01 课：最小节点（Python 版）。

演示一个节点的最小骨架：
    1. 继承 rclpy.node.Node
    2. 在构造函数里创建定时器（心跳）
    3. main() 中 init -> spin -> shutdown

运行:
    ros2 run minimal_node hello_node
"""

import rclpy
from rclpy.node import Node


class HelloNode(Node):
    """一个每秒打印一次心跳的节点。"""

    def __init__(self):
        # 参数是「节点名」，它是图中的唯一标识（可被命名空间前缀）。
        super().__init__('hello_node')

        # 心跳计数。
        self._count = 0

        # 每 1.0 秒触发一次回调。这是节点的「心跳」。
        self._timer = self.create_timer(1.0, self._on_timer)

        self.get_logger().info('HelloNode 启动！')

    def _on_timer(self):
        """定时器回调：打印心跳。"""
        self._count += 1
        self.get_logger().info(
            f'Hello ROS 2! 心跳 #{self._count} '
            f'(节点名: {self.get_name()}, 命名空间: {self.get_namespace()})'
        )


def main(args=None):
    # 初始化 ROS 2 客户端库。
    rclpy.init(args=args)

    node = HelloNode()
    try:
        # spin：阻塞运行事件循环，直到 Ctrl+C。
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # 清理资源。
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
