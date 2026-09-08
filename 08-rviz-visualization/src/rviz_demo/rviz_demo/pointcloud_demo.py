"""第 08 课：点云可视化演示。

生成一片「正弦波动」的彩色点云发布到 /pointcloud_demo。
演示 PointCloud2 的字段布局与打包方法。

运行:
    ros2 run rviz_demo pointcloud_demo
"""

import math

import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2, PointField
from sensor_msgs_py import point_cloud2
from std_msgs.msg import Header


class PointCloudDemo(Node):

    def __init__(self):
        super().__init__('pointcloud_demo')
        self._pub = self.create_publisher(PointCloud2, 'pointcloud_demo', 10)
        self._t = 0.0
        self._timer = self.create_timer(0.1, self._publish)  # 10 Hz
        self.get_logger().info('PointCloudDemo 已启动，打开 RViz 查看 /pointcloud_demo')

    def _publish(self):
        self._t += 0.1
        # 在 4m x 4m 网格上生成点，z = 正弦波（随时间流动）
        xs, ys = np.meshgrid(
            np.linspace(-2, 2, 40), np.linspace(-2, 2, 40))
        zs = 0.3 * np.sin(xs * 2.0 + self._t) + 0.3 * np.cos(ys * 2.0 + self._t)
        points = np.stack([xs, ys, zs], axis=-1).reshape(-1, 3).tolist()

        # 定义点云字段：每个点 3 个 float32（x、y、z）
        fields = [
            PointField(name='x', offset=0, datatype=PointField.FLOAT32, count=1),
            PointField(name='y', offset=4, datatype=PointField.FLOAT32, count=1),
            PointField(name='z', offset=8, datatype=PointField.FLOAT32, count=1),
        ]

        header = Header()
        header.frame_id = 'map'
        header.stamp = self.get_clock().now().to_msg()

        # 打包成 PointCloud2
        cloud = point_cloud2.create_cloud(header, fields, points)
        self._pub.publish(cloud)


def main(args=None):
    rclpy.init(args=args)
    node = PointCloudDemo()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
