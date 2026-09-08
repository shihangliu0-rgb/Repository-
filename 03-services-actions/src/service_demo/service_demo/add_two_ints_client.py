"""第 03 课：客户端 —— 调用两数相加服务。

用法:
    ros2 run service_demo add_two_ints_client          # 默认 41 + 1
    ros2 run service_demo add_two_ints_client 3 4      # 自定义两个整数
"""

import sys

import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class AddTwoIntsClient(Node):

    def __init__(self):
        super().__init__('add_two_ints_client')
        self._cli = self.create_client(AddTwoInts, 'add_two_ints')

    def call(self, a: int, b: int) -> int:
        # 等待服务上线（最多 10 秒）
        if not self._cli.wait_for_service(timeout_sec=10.0):
            raise RuntimeError('服务 /add_two_ints 未上线（服务端运行了吗？）')

        request = AddTwoInts.Request()
        request.a = a
        request.b = b

        # call_async 返回 Future；spin_until_future_complete 阻塞到拿到应答
        future = self._cli.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=10.0)
        if future.result() is None:
            raise RuntimeError(f'服务调用失败: {future.exception()}')
        return future.result().sum


def main(args=None):
    a, b = 41, 1
    if len(sys.argv) >= 3:
        a, b = int(sys.argv[1]), int(sys.argv[2])

    rclpy.init(args=args)
    node = AddTwoIntsClient()
    try:
        result = node.call(a, b)
        node.get_logger().info(f'应答: {a} + {b} = {result}')
    except RuntimeError as e:
        node.get_logger().error(str(e))
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
