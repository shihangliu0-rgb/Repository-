# 第 08 课 · RViz 高级可视化：Marker 与点云

> **目标**：学会向 RViz 发布两类「自定义可视化」——
> **Marker**（箭头、立方体、文字、轨迹线等几何图形）和 **PointCloud2**（点云）。
> 这是调试导航路径、机械臂轨迹、感知结果的必备技能。

## 1. 本课概念

- **visualization_msgs/Marker**：RViz 的「万能画笔」。`type` 字段决定形状：
  `ARROW / CUBE / SPHERE / CYLINDER / LINE_STRIP / TEXT_VIEW_FACING / MESH_RESOURCE`…
  每个 Marker 有 `ns`（命名空间）+ `id` 唯一标识，`action` 决定增/删/改。
- **visualization_msgs/MarkerArray**：一次发一批 Marker。
- **sensor_msgs/PointCloud2**：点云。核心是 `fields`（每点的字段布局，如 x、y、z）
  和一段紧凑的二进制 `data`。本课用 numpy 生成、`sensor_msgs_py.point_cloud2` 打包。
- **frame_id**：所有可视化都要落在某个坐标系里。本课统一用 `map`，RViz 的 Fixed Frame 也是 `map`。

## 2. 编译与运行

```bash
cd 08-rviz-visualization
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash

# 一条命令：起两个发布节点 + 打开配好的 RViz
ros2 launch rviz_demo visualize.launch.py
```

RViz 里应看到：
- 一个旋转的立方体 + 一个跳动的小球 + 一个指向前方的箭头；
- 一行立体文字 "HELLO ROS2"；
- 一条旋转的螺旋轨迹线；
- 一片正弦波动的彩色点云。

## 3. 分节点运行（理解每个组件）

```bash
# 终端 1 / 2 / 3 分别起，再开一个终端起 rviz
ros2 run rviz_demo marker_demo
ros2 run rviz_demo pointcloud_demo
rviz2 -d install/rviz_demo/share/rviz_demo/rviz/visualize.rviz
```

用 `ros2 topic list` 能看到 `/marker_demo`（MarkerArray）和 `/pointcloud_demo`（PointCloud2）。

## 4. 动手练习

1. **改颜色与尺寸**：把立方体改成半透明绿色（`color.a = 0.5`）。
2. **加一个 MESH**：RViz 支持 `.dae`/`.stl`，尝试 `type=MESH_RESOURCE` 加载一个模型。
3. **轨迹追踪**：修改 `marker_demo.py`，让 `LINE_STRIP` 记录并画出一个移动小球的轨迹。
4. （挑战）写一个节点，订阅 `/scan`（如果第 07 课仿真在跑），把每个激光点画成 Marker 小球。

## 5. 关键代码导读

- `marker_demo.py` 里 `make_marker()` 是通用工厂函数：填好 `header / ns / id / type / action / pose / scale / color`
  就是一个合法 Marker。**id 冲突**是最常见的坑——同 `ns` 同 `id` 会被覆盖。
- `pointcloud_demo.py` 里重点看 `create_cloud_xyz32()`：
  定义 `fields`（x、y、z 的偏移与类型）→ 用 `point_cloud2.create_cloud()` 把点列表打包。

## 6. 常见问题

- **RViz 里什么都不显示**：检查 Fixed Frame 是否是 `map`；两个节点是否在运行
  （`ros2 topic hz /marker_demo`）。
- **Marker 只显示一个**：`ns`/`id` 重复了，后面的覆盖了前面的。
- **点云不显示/报 `frame [map] does not exist`**：本课没有发布 `map` 坐标系的 TF。
  因为只发可视化、不涉及真实机器人，RViz 允许「无 TF 直接按坐标画」；若报警告可忽略，
  或加一条静态变换：`ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 map world`。

## 7. 下一课

[../09-slam-mapping](../09-slam-mapping/)：真刀真枪——在仿真里边开车边建图（SLAM）。
