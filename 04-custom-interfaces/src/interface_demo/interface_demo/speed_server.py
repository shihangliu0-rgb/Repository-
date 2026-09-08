"""第 04 课：提供自定义服务 custom_interfaces/srv/SetSpeed。

运行:
    ros2 run interface_demo speed_server

另开终端调用:
    ros2 service call /set_speed custom_interfaces/srv/SetSpeed \\
        "{linear_x: 0.5, angular_z: 0.3}"
"""

import rclpy
from rclpy.node import Node

from custom_interfaces.srv import SetSpeed


class SpeedServer(Node):

    # 简单的“限速”规则，演示服务端的业务逻辑
    MAX_LINEAR = 1.0
    MAX_ANGULAR = 2.0

    def __init__(self):
        super().__init__('speed_server')
        self._srv = self.create_service(SetSpeed, 'set_speed', self._on_request)
        self.get_logger().info('服务 /set_speed 已就绪……')

    def _on_request(self, request: SetSpeed.Request, response: SetSpeed.Response):
        if abs(request.linear_x) > self.MAX_LINEAR:
            response.success = False
            response.message = (
                f'线速度 {request.linear_x:.2f} 超过上限 {self.MAX_LINEAR:.2f}')
        elif abs(request.angular_z) > self.MAX_ANGULAR:
            response.success = False
            response.message = (
                f'角速度 {request.angular_z:.2f} 超过上限 {self.MAX_ANGULAR:.2f}')
        else:
            response.success = True
            response.message = (
                f'速度已设置: linear_x={request.linear_x}, angular_z={request.angular_z}')
            # 真实项目中这里会把速度发给底盘控制器

        self.get_logger().info(f'{response.message} (success={response.success})')
        return response


def main(args=None):
    rclpy.init(args=args)
    node = SpeedServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
