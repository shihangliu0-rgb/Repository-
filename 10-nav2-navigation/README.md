# 第 10 课 · Nav2 导航（毕业课）

> **目标**：在已知地图上，让机器人「**你点一个目标，它自己规划路径、避开障碍、开过去**」。
> 这是移动机器人软件栈的集大成：定位 + 建图 + 规划 + 控制 + 安全。

## 1. 本课概念（这张图值得背下来）

```
                       给定地图 (learn_map.yaml)
                              │
                              ▼
                        ┌─ map_server ──── /map
                        │
   /scan ──► AMCL 粒子滤波定位 ──► TF: map→odom（把“我在地图哪里”接上里程计）
                        │
                        ▼
     ┌────────────── Nav2 ──────────────┐
     │  planner_server   全局规划：地图上找一条路（NavfnPlanner）
     │  controller_server 局部控制：沿路径走并实时避障（DWB）
     │  behavior_server  恢复行为：卡住了就转圈/倒退再试
     │  bt_navigator     行为树：把上面这些串成“导航到目标”的流程
     │  velocity_smoother + collision_monitor：速度平滑 + 碰撞急停
     └──────────────────────────────────┘
                        │
                        ▼  /cmd_vel
            diff_drive_controller（第 07 课的仿真底盘）
```

- **全局代价地图**：整张地图 + 膨胀层（离障碍物越近代价越高，规划器自然远离墙）。
- **局部代价地图**：3m×3m 滚动窗口，用实时雷达更新，处理地图上没有的新障碍。
- **AMCL**：粒子滤波。初始要大概知道自己在哪（本课参数已预设出生点 (-2, 0)）。

## 2. 编译与运行

```bash
cd 10-nav2-navigation
rosdep install --from-paths src --ignore-src -r -y    # 会装上 navigation2 / nav2_bringup
colcon build --symlink-install
source install/setup.bash

# 一条命令：仿真 + 地图 + Nav2 + RViz 全部拉起
ros2 launch nav2_demo navigation.launch.py
```

启动需要 30 秒~1 分钟（Nav2 节点逐个上线），等终端不再刷屏、RViz 出现地图与机器人。

## 3. 开始导航！

1. RViz 里应能看到：灰色地图 + 机器人 + 两个彩色代价地图圆圈。
2. 点工具栏 **Nav2 Goal**（绿色旗子），在地图空白处点一下、拖动方向、松开。
3. 看机器人出发：紫色全局路径 → 边走边局部避障 → 到达目标。
4. 试试把目标点设在红色箱子另一侧 —— 观察它如何绕障。
5. **定位不准了？**（机器人位置与真实不符）：点 **2D Pose Estimate**，在机器人真实位置
   按一下并拖动朝向，粒子会重新收敛。

命令行也能发目标（等价于 RViz 点击）：

```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: map}, pose: {position: {x: 3.0, y: 3.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

## 4. 用你自己建的地图（联动第 09 课）

```bash
ros2 launch nav2_demo navigation.launch.py map:=/path/to/my_map.yaml
```

注意：地图必须和当前世界匹配（就是你在第 09 课建的那张），否则定位永远对不上。

## 5. 验证清单

```bash
ros2 topic list      # /map /amcl_pose /plan /cmd_vel /cmd_vel_smoothed 都应该在
ros2 node list       # amcl / bt_navigator / controller_server / planner_server ...
ros2 topic echo /amcl_pose --once   # 机器人在地图中的估计位姿
```

## 6. 作业

1. **巡航**：用 `ros2 action send_goal /follow_waypoints nav2_msgs/action/FollowWaypoints`
   让机器人依次经过 3 个点。
2. **动态避障**：导航途中在 Gazebo 里手动拖一个箱子到路径上（选中物体→拖动），
   观察局部代价地图与路径重规划。
3. **调参实验**：把 `inflation_radius` 从 0.55 调到 0.30，对比路径离墙的远近。
4. （挑战）把 `max_vel_x` 提到 0.8，观察是否容易撞/卡；再改回来，理解「参数匹配」。

## 7. 常见问题

- **RViz 里机器人在地图外/不动**：定位没收敛。点 **2D Pose Estimate** 在真实位置校正；
  确认地图和世界匹配、`initial_pose` 参数与出生点一致。
- **一直转圈不走**：`ros2 node list` 检查节点是否齐全；看终端有无 `Timed out`；
  常见于某节点参数缺失——对照官方 `nav2_bringup/params/nav2_params.yaml` 检查。
- **路径穿过障碍物**：全局代价地图没加载静态层？确认 `/map` 正常、`track_unknown_space` 配置。
- **`bringup_launch.py` 报参数错误（不同 Nav2 小版本差异）**：
  保底方案——直接用官方默认参数：
  ```bash
  ros2 launch nav2_bringup bringup_launch.py \
    map:=install/nav2_demo/share/nav2_demo/maps/learn_map.yaml use_sim_time:=true
  ```

## 8. 毕业之后

你已经打通「建模 → 仿真 → 感知 → 建图 → 定位 → 导航」全链路。
回到仓库根目录的 [PLAN.md](../PLAN.md) 看「结业检验」与进阶方向吧。
