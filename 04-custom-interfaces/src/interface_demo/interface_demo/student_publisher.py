"""第 04 课：发布自定义消息 custom_interfaces/msg/StudentInfo。

运行:
    ros2 run interface_demo student_publisher
"""

import rclpy
from rclpy.node import Node

# 导入路径规律：<接口包名>.msg.<消息名>
from custom_interfaces.msg import StudentInfo


class StudentPublisher(Node):

    # 模拟的三名学生，循环发布
    STUDENTS = [
        ('张三', 20, 92.5),
        ('李四', 21, 85.0),
        ('王五', 19, 78.5),
    ]

    def __init__(self):
        super().__init__('student_publisher')
        self._pub = self.create_publisher(StudentInfo, 'student_info', 10)
        self._index = 0
        # 每 2 秒发布一条
        self._timer = self.create_timer(2.0, self._on_timer)
        self.get_logger().info('开始发布 StudentInfo 消息……')

    def _on_timer(self):
        name, age, score = self.STUDENTS[self._index]
        self._index = (self._index + 1) % len(self.STUDENTS)

        msg = StudentInfo()
        msg.name = name
        msg.age = age
        msg.score = score

        self._pub.publish(msg)
        self.get_logger().info(f'发布: name={msg.name}, age={msg.age}, score={msg.score}')


def main(args=None):
    rclpy.init(args=args)
    node = StudentPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
