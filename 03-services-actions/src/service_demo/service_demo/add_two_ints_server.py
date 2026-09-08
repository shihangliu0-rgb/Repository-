"""第 03 课：服务端 —— 两数相加。

提供 /add_two_ints 服务，接口类型 example_interfaces/srv/AddTwoInts：
    请求: int64 a, int64 b
    应答: int64 sum

运行:
    ros2 run service_demo add_two_ints_server
"""

import rclpy
from rclpy.node import Node
from example_interfaces.srv import AddTwoInts


class AddTwoIntsServer(Node):

    def __init__(self):
        super().__init__('add_two_ints_server')
        # create_service(接口类型, 服务名, 回调)
        self._srv = self.create_service(AddTwoInts, 'add_two_ints', self._on_request)
        self.get_logger().info('服务 /add_two_ints 已就绪，等待请求……')

    def _on_request(self, request: AddTwoInts.Request, response: AddTwoInts.Response):
        """服务回调：收到请求 -> 计算 -> 填充应答并返回。"""
        response.sum = request.a + request.b
        self.get_logger().info(f'收到请求: {request.a} + {request.b} -> {response.sum}')
        return response


def main(args=None):
    rclpy.init(args=args)
    node = AddTwoIntsServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
