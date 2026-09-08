"""第 05 课：带参数的 listener。

参数:
    prefix (string): 打印前缀，默认 "[收到]"
"""

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class ParamListener(Node):

    def __init__(self):
        super().__init__('listener')
        self.declare_parameter('prefix', '[收到]')
        self._sub = self.create_subscription(
            String, 'chatter', self._on_message, 10)
        self.get_logger().info('Listener 已启动，正在监听 /chatter……')

    def _on_message(self, msg: String):
        prefix = self.get_parameter('prefix').value
        self.get_logger().info(f'{prefix} {msg.data}')


def main(args=None):
    rclpy.init(args=args)
    node = ParamListener()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
