"""第 03 课：Action 客户端 —— 请求 Fibonacci 数列并实时打印反馈。

用法:
    ros2 run service_demo fibonacci_action_client          # 默认请求 10 个数
"""

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from example_interfaces.action import Fibonacci


class FibonacciActionClient(Node):

    def __init__(self):
        super().__init__('fibonacci_action_client')
        self._client = ActionClient(self, Fibonacci, 'fibonacci')
        self._goal_done = False

    def send_goal(self, order: int):
        self.get_logger().info(f'等待 Action 服务 /fibonacci 上线……')
        if not self._client.wait_for_server(timeout_sec=10.0):
            raise RuntimeError('Action 服务未上线（服务端运行了吗？）')

        goal = Fibonacci.Goal()
        goal.order = order
        self.get_logger().info(f'发送目标: order={order}')

        # send_goal_async 立即返回一个「发送结果」的 future；
        # feedback_callback 会在任务执行期间被反复调用。
        future = self._client.send_goal_async(
            goal, feedback_callback=self._on_feedback)
        future.add_done_callback(self._on_goal_accepted)

    def _on_feedback(self, feedback_msg):
        """每收到一条进度反馈就调用一次。"""
        self.get_logger().info(f'反馈: {feedback_msg.feedback.sequence}')

    def _on_goal_accepted(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warning('目标被拒绝')
            self._goal_done = True
            return
        self.get_logger().info('目标已被接受，等待最终结果……')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self._on_result)

    def _on_result(self, future):
        result = future.result().result
        self.get_logger().info(f'结果: {result.sequence}')
        self._goal_done = True


def main(args=None):
    rclpy.init(args=args)
    node = FibonacciActionClient()
    try:
        node.send_goal(10)
        # 一直 spin 直到结果返回
        while rclpy.ok() and not node._goal_done:
            rclpy.spin_once(node, timeout_sec=0.5)
    except RuntimeError as e:
        node.get_logger().error(str(e))
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
