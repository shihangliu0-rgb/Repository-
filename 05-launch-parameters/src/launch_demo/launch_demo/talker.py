"""第 05 课：带参数的 talker。

参数:
    message (string):           要发布的文本，默认 "Hello from launch_demo"
    publish_frequency (double): 发布频率 Hz，默认 1.0

支持运行时用 `ros2 param set` 动态修改，立即生效。
"""

import rclpy
from rclpy.node import Node
from rcl_interfaces.msg import SetParametersResult
from std_msgs.msg import String


class ParamTalker(Node):

    def __init__(self):
        super().__init__('talker')

        # 1) 声明参数并给默认值（必须在读取之前声明）
        self.declare_parameter('message', 'Hello from launch_demo')
        self.declare_parameter('publish_frequency', 1.0)

        self._pub = self.create_publisher(String, 'chatter', 10)
        self._count = 0

        # 2) 注册参数变更回调：`ros2 param set` 时会先过这里
        self.add_on_set_parameters_callback(self._on_params_changed)

        # 3) 按参数创建定时器
        self._rebuild_timer()
        self.get_logger().info(
            f'Talker 已启动: message="{self.message}", 频率={self.frequency}Hz')

    @property
    def message(self) -> str:
        return self.get_parameter('message').value

    @property
    def frequency(self) -> float:
        return self.get_parameter('publish_frequency').value

    def _rebuild_timer(self):
        """（重新）按当前频率创建定时器。"""
        if hasattr(self, '_timer') and self._timer is not None:
            self._timer.cancel()
            self.destroy_timer(self._timer)
        period = 1.0 / max(self.frequency, 0.01)
        self._timer = self.create_timer(period, self._on_timer)

    def _on_params_changed(self, params):
        """参数热更新回调：校验 -> 接受 -> 视情况重建定时器。"""
        for p in params:
            if p.name == 'publish_frequency':
                if p.value <= 0:
                    return SetParametersResult(
                        successful=False, reason='频率必须大于 0')
                self.get_logger().info(f'频率改为 {p.value}Hz，重建定时器')
        # 注意：回调返回时参数还没真正写入，用定时器下一拍读取即可；
        # 频率变化时需要重建定时器，这里简单地在写回后重建。
        self._need_rebuild = True
        return SetParametersResult(successful=True)

    def _on_timer(self):
        if getattr(self, '_need_rebuild', False):
            self._need_rebuild = False
            self._rebuild_timer()
            return
        msg = String()
        msg.data = f'{self.message} #{self._count}'
        self._pub.publish(msg)
        self.get_logger().info(f'发布: {msg.data}')
        self._count += 1


def main(args=None):
    rclpy.init(args=args)
    node = ParamTalker()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
