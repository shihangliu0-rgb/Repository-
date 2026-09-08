# 第 09 课 · SLAM 建图

> **目标**：在仿真里**边遥控边建图**（slam_toolbox），看着地图实时生长，最后把地图保存成文件。
> 这张地图就是第 10 课导航用的「已知环境」。

## 1. 本课概念

- **SLAM**（Simultaneous Localization And Mapping，同时定位与建图）：机器人在未知环境里，
  一边估计自己在哪（定位），一边绘制环境（建图）。输入 = **里程计 + 激光雷达**，输出 = **栅格地图**。
- **slam_toolbox**：ROS 2 事实标准的 2D SLAM。本仓库用 `online_async` 模式
  （在线、异步、适合建图，能处理回环）。
- **TF 链**：建图时多了一环 `map -> odom`，由 slam_toolbox 发布。
  完整链：`map -> odom -> base_link -> lidar_link`。
- **地图 = 2 个文件**：`.pgm`（图像，黑=障碍、白=空闲、灰=未知）+ `.yaml`（分辨率、原点等元数据）。

## 2. 编译与运行

```bash
cd 09-slam-mapping
rosdep install --from-paths src --ignore-src -r -y    # 会装上 slam_toolbox、nav2_map_server
colcon build --symlink-install
source install/setup.bash

# 终端 1：一键启动 仿真 + SLAM + RViz
ros2 launch slam_demo slam.launch.py
```

RViz 里 `Fixed Frame = map`，能看到 `/map`（灰色未知区）和红色激光点。

```bash
# 终端 2：键盘遥控
ros2 run learn_gazebo teleop_twist.py
```

## 3. 建图操作要领（重要）

1. **慢慢开、贴着墙走**：让雷达尽量扫到所有障碍物。
2. **走遍每个角落**，尤其墙角和障碍物背面；回到起点附近可以触发**回环校正**。
3. 观察 RViz：走过的地方变白/黑，地图随 `map_update_interval` 刷新。
4. 开得太快或原地猛转会让匹配失败、地图错位——体会「里程计漂移」和「扫描匹配」的关系。

> 小技巧：`slam_toolbox` 的参数 `minimum_travel_distance: 0.5` 表示移动 0.5m 才更新一次，
> 想看得更实时可改小到 `0.1` 后重新编译。

## 4. 保存地图

建完图后（另开终端，记得 source）：

```bash
# 保存到你想要的目录，例如工作空间根目录
ros2 run nav2_map_server map_saver_cli -f my_map
# 生成两个文件：my_map.pgm + my_map.yaml
```

用图片查看器打开 `my_map.pgm`，看看你建的地图。`my_map.yaml` 内容类似：

```yaml
image: my_map.pgm
mode: trinary
resolution: 0.05
origin: [-5.05, -5.05, 0]
negate: 0
occupied_thresh: 0.65
free_thresh: 0.25
```

## 5. 验证

```bash
ros2 topic list                 # 应有 /map /map_metadata
ros2 topic echo /map_metadata --once   # 分辨率 0.05、宽高
ros2 run tf2_ros tf2_echo map odom     # slam_toolbox 在发布这条变换
```

## 6. 作业

1. 把 `map_update_interval` 从 5.0 改到 1.0，重新编译，感受地图刷新变快。
2. 把 `resolution` 改成 0.02，重建一次图，对比地图文件大小与精细度。
3. 故意快速原地转几圈，观察地图错位，再用慢速走直线恢复——理解扫描匹配。
4. （挑战）保存两张不同的地图（不同世界或不同走法），用图片工具对比。

## 7. 常见问题

- **地图一直不更新/全灰**：`ros2 topic hz /scan` 有没有数据？`tf2_echo map odom` 是否输出？
  常见原因是 `use_sim_time` 不一致或 `base_frame` 写错（必须是 `base_footprint`）。
- **地图严重错位**：开太快、转太猛；放慢速度重建。也可减小 `minimum_travel_distance`。
- **`map_saver_cli` 报错找不到**：没装 `nav2_map_server`，跑一次 `rosdep install`。

## 8. 下一课

[../10-nav2-navigation](../10-nav2-navigation/)：在已知地图上实现自主导航——给个目标点，机器人自己开过去。
