"""第 03 课：Action 服务端 —— 生成 Fibonacci 数列。

接口 example_interfaces/action/Fibonacci：
    goal:     int32 order          （要生成多少个数）
    feedback: int32[] sequence     （当前已生成的部分序列）
    result:   int32[] sequence     （最终完整序列）

运行:
    ros2 run service_demo fibonacci_action_server
"""

import time

import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from example_interfaces.action import Fibonacci


class FibonacciActionServer(Node):

    def __init__(self):
        super().__init__('fibonacci_action_server')
        # ActionServer 会自动创建三个底层通道：
        #   /fibonacci/_action/send_goal | feedback | get_result
        self._server = ActionServer(
            self,
            Fibonacci,
            'fibonacci',
            execute_callback=self._execute,
        )
        self.get_logger().info('Action 服务 /fibonacci 已就绪……')

    def _execute(self, goal_handle):
        """长任务主体：边算边发布反馈，全部算完后返回结果。"""
        self.get_logger().info(f'收到目标: 生成 {goal_handle.request.order} 个数')

        feedback = Fibonacci.Feedback()
        sequence = [0, 1]

        # 逐步计算，每步发布一次「进度」
        for _ in range(1, goal_handle.request.order):
            sequence.append(sequence[-1] + sequence[-2])
            feedback.sequence = sequence
            goal_handle.publish_feedback(feedback)
            time.sleep(0.5)      # 模拟耗时过程，便于观察反馈

        # 任务完成：succeed 并返回结果
        goal_handle.succeed()
        result = Fibonacci.Result()
        result.sequence = sequence
        self.get_logger().info('任务完成，返回结果')
        return result


def main(args=None):
    rclpy.init(args=args)
    node = FibonacciActionServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
