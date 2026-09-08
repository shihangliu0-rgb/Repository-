"""第 08 课：Marker 可视化演示。

向 /marker_demo 话题发布一批 Marker，展示常用类型：
    - CUBE              旋转的立方体
    - SPHERE            上下跳动的小球
    - ARROW            指向前方的箭头
    - TEXT_VIEW_FACING  立体文字
    - LINE_STRIP        螺旋轨迹线

运行:
    ros2 run rviz_demo marker_demo
"""

import math

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Point, Quaternion
from std_msgs.msg import ColorRGBA
from visualization_msgs.msg import Marker, MarkerArray


def make_marker(marker_type, ns, marker_id, action=Marker.ADD):
    """Marker 工厂：填好公共字段。"""
    m = Marker()
    m.header.frame_id = 'map'
    m.header.stamp.sec = 0
    m.header.stamp.nanosec = 0
    m.ns = ns
    m.id = marker_id
    m.type = marker_type
    m.action = action
    m.pose.orientation = Quaternion(w=1.0)
    m.scale.x = m.scale.y = m.scale.z = 0.2
    m.color = ColorRGBA(r=1.0, g=1.0, b=1.0, a=1.0)
    m.lifetime.sec = 0  # 0 = 永久，靠每次发布刷新
    return m


class MarkerDemo(Node):

    def __init__(self):
        super().__init__('marker_demo')
        self._pub = self.create_publisher(MarkerArray, 'marker_demo', 10)
        self._t = 0.0
        self._timer = self.create_timer(0.05, self._publish)  # 20 Hz
        self.get_logger().info('MarkerDemo 已启动，打开 RViz 查看 /marker_demo')

    def _publish(self):
        self._t += 0.05
        t = self._t
        arr = MarkerArray()

        # 1) 旋转的立方体（绕 z 轴）
        cube = make_marker(Marker.CUBE, 'shapes', 0)
        cube.pose.position = Point(x=0.0, y=0.0, z=0.5)
        angle = t
        cube.pose.orientation = Quaternion(
            x=0.0, y=0.0, z=math.sin(angle / 2), w=math.cos(angle / 2))
        cube.scale.x = cube.scale.y = cube.scale.z = 0.5
        cube.color = ColorRGBA(r=0.2, g=0.6, b=1.0, a=1.0)
        arr.markers.append(cube)

        # 2) 上下跳动的小球
        sphere = make_marker(Marker.SPHERE, 'shapes', 1)
        sphere.pose.position = Point(x=1.0, y=0.0, z=0.5 + 0.4 * abs(math.sin(t * 2)))
        sphere.color = ColorRGBA(r=1.0, g=0.4, b=0.1, a=1.0)
        arr.markers.append(sphere)

        # 3) 指向 +x 的箭头（起点 -> 终点）
        arrow = make_marker(Marker.ARROW, 'shapes', 2)
        arrow.points = [Point(x=-1.0, y=0.0, z=0.2), Point(x=-0.2, y=0.0, z=0.2)]
        arrow.scale.x = 0.05  # 箭杆粗细
        arrow.scale.y = 0.12  # 箭头粗细
        arrow.color = ColorRGBA(r=0.1, g=0.9, b=0.3, a=1.0)
        arr.markers.append(arrow)

        # 4) 立体文字
        text = make_marker(Marker.TEXT_VIEW_FACING, 'text', 0)
        text.pose.position = Point(x=0.0, y=1.5, z=0.8)
        text.scale.z = 0.4  # 文字高度
        text.text = 'HELLO ROS2'
        text.color = ColorRGBA(r=1.0, g=1.0, b=0.2, a=1.0)
        arr.markers.append(text)

        # 5) 螺旋轨迹线（LINE_STRIP，用 points 列表画折线）
        line = make_marker(Marker.LINE_STRIP, 'trajectory', 0)
        line.scale.x = 0.03  # 线宽
        line.color = ColorRGBA(r=0.9, g=0.2, b=0.9, a=1.0)
        for i in range(200):
            a = i * 0.08 + t
            line.points.append(Point(
                x=-1.5 + 0.8 * math.cos(a),
                y=1.5 + 0.8 * math.sin(a),
                z=0.1 + i * 0.008))
        arr.markers.append(line)

        self._pub.publish(arr)


def main(args=None):
    rclpy.init(args=args)
    node = MarkerDemo()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
