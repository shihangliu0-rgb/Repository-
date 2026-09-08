"""第 02 课：订阅者（listener）。

订阅话题 /chatter，打印收到的 std_msgs/msg/String 消息。

运行:
    ros2 run talker_listener listener
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class Listener(Node):

    def __init__(self):
        super().__init__('listener')
        # 订阅 /chatter；每来一条消息就调用 _on_message。
        self._sub = self.create_subscription(
            String, 'chatter', self._on_message, 10)
        self.get_logger().info('Listener 已上线，正在监听 /chatter……')

    def _on_message(self, msg: String):
        self.get_logger().info(f'收到: {msg.data}')


def main(args=None):
    rclpy.init(args=args)
    node = Listener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
