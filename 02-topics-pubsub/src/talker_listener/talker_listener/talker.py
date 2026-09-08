"""第 02 课：发布者（talker）。

以 1 Hz 频率向话题 /chatter 发布 std_msgs/msg/String 消息。

运行:
    ros2 run talker_listener talker
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Talker(Node):

    def __init__(self):
        super().__init__('talker')

        # create_publisher(消息类型, 话题名, QoS 深度)
        # 话题名不写前导 '/' 时为「相对名」，实际解析为 /chatter。
        self._pub = self.create_publisher(String, 'chatter', 10)

        self._count = 0
        self._timer = self.create_timer(1.0, self._on_timer)
        self.get_logger().info('Talker 已上线，正在向 /chatter 发布消息……')

    def _on_timer(self):
        msg = String()
        msg.data = f'Hello from talker #{self._count}'
        self._pub.publish(msg)
        self.get_logger().info(f'发布: {msg.data}')
        self._count += 1


def main(args=None):
    rclpy.init(args=args)
    node = Talker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
