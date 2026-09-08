"""第 04 课：调用自定义服务 custom_interfaces/srv/SetSpeed。

用法:
    ros2 run interface_demo speed_client              # 默认 0.5 / 0.3
    ros2 run interface_demo speed_client 0.2 0.1
"""

import sys

import rclpy
from rclpy.node import Node

from custom_interfaces.srv import SetSpeed


class SpeedClient(Node):

    def __init__(self):
        super().__init__('speed_client')
        self._cli = self.create_client(SetSpeed, 'set_speed')

    def call(self, linear_x: float, angular_z: float) -> SetSpeed.Response:
        if not self._cli.wait_for_service(timeout_sec=10.0):
            raise RuntimeError('服务 /set_speed 未上线（先运行 speed_server）')

        request = SetSpeed.Request()
        request.linear_x = linear_x
        request.angular_z = angular_z

        future = self._cli.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=10.0)
        if future.result() is None:
            raise RuntimeError(f'服务调用失败: {future.exception()}')
        return future.result()


def main(args=None):
    linear_x, angular_z = 0.5, 0.3
    if len(sys.argv) >= 3:
        linear_x, angular_z = float(sys.argv[1]), float(sys.argv[2])

    rclpy.init(args=args)
    node = SpeedClient()
    try:
        response = node.call(linear_x, angular_z)
        level = 'info' if response.success else 'warn'
        getattr(node.get_logger(), level)(
            f'应答: success={response.success}, message="{response.message}"')
    except RuntimeError as e:
        node.get_logger().error(str(e))
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
