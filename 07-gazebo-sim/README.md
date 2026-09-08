# 第 07 课 · Gazebo 仿真

> **目标**：把第 06 课的机器人放进 Gazebo 物理仿真世界，用键盘遥控它移动，并读取激光雷达数据。
> 这是后面 SLAM 和导航课的基础设施。

## 1. 本课概念（先读懂这张图再动手）

```
                     ROS 2 域                                  Gazebo 域
 ┌──────────────────────────────────────────┐    ┌──────────────────────────────┐
 │ teleop_twist.py ──► /cmd_vel             │    │                              │
 │                          │               │    │   gz_ros2_control 插件        │
 │  (重映射) /diff_drive.../cmd_vel_unstamped├────┼─► 物理仿真轮子转动             │
 │                          │               │    │        │                     │
 │ diff_drive_controller    │               │    │   gpu_lidar 传感器            │
 │  ├─► /odom (里程计)       │               │    │        │ /scan (gz 话题)      │
 │  └─► TF: odom→base_link  │               │    │        ▼                     │
 │                          │               │    │                              │
 │ joint_state_broadcaster  │               │    └──────────┬───────────────────┘
 │  └─► /joint_states       │               │               │ ros_gz_bridge
 │         │                │               │   /clock ◄────┤
 │         ▼                │               │   /scan  ◄────┘
 │ robot_state_publisher    │               │
 │  └─► TF: base_link→轮/雷达 │               │
 └──────────────────────────────────────────┘
```

- **ros2_control**：ROS 2 的控制器框架。`diff_drive_controller` 把「线速度/角速度」换算成
  「左右轮转速」，同时积分出里程计 `/odom`。
- **gz_ros2_control**：把上面的控制器插进 Gazebo，仿真里的轮子就听控制器指挥。
- **ros_gz_bridge**：Gazebo 与 ROS 2 的消息翻译官。本课只桥接 `/clock`（仿真时钟）和 `/scan`（雷达）。
- **use_sim_time**：仿真时所有节点必须用仿真时钟，否则时间戳错乱、TF 全崩。

## 2. 编译与运行

```bash
cd 07-gazebo-sim
rosdep install --from-paths src --ignore-src -r -y    # 会装上 gz、ros2_control、控制器等
colcon build --symlink-install
source install/setup.bash

# 终端 1：启动仿真
ros2 launch learn_gazebo sim.launch.py
```

等 Gazebo 窗口出来、机器人出现后：

```bash
# 终端 2：键盘遥控（按键见屏幕提示：i 前进 , 后退 j/l 转向）
ros2 run learn_gazebo teleop_twist.py
```

```bash
# 终端 3（可选）：RViz 里看雷达点云与里程计箭头
rviz2 -d install/learn_gazebo/share/learn_gazebo/rviz/sim.rviz --ros-args -p use_sim_time:=true
```

## 3. 验证清单（逐项检查，这是后面课程的地基）

```bash
ros2 topic list
# 必须看到: /cmd_vel  /odom  /scan  /joint_states  /tf  /clock

ros2 topic echo /scan --once | head        # 雷达数据，frame_id 应为 lidar_link
ros2 topic hz /scan                        # 约 10 Hz（URDF 里 update_rate）
ros2 topic echo /odom --once | head        # 里程计，frame_id 应为 odom

ros2 run tf2_ros tf2_echo odom base_link   # 开车时数值应随运动变化
ros2 controller list                       # 两个控制器都应是 active 状态
```

遥控开车时：`/odom` 的 position 在变，RViz 里机器人模型跟着动 —— 恭喜，仿真链路全通。

## 4. 作业

1. 把机器人出生点改到 `(0, 0)`（编辑 `sim.launch.py` 里 `spawn_robot` 的参数）。
2. 在 `simple_world.sdf` 里加一堵墙，重新编译后观察 `/scan` 数据变化。
3. 写一个「自动画圆」节点：定时向 `/cmd_vel` 发布固定 twist（提示：参考第 02 课的定时器写法）。
4. （挑战）把 `learnbot_controllers.yaml` 的 `wheel_separation` 故意改错 20%，
   开车画一个圈，观察 `/odom` 和真实位姿的偏差——理解「参数标定」为什么重要。

## 5. 常见问题

- **Gazebo 打开后没有机器人**：看终端日志 `create` 是否报错；确认 `robot_state_publisher`
  在运行（`ros2 topic info /robot_description` 应有发布者）。可手动补一次
  `ros2 run ros_gz_sim create -topic robot_description -name learning_bot`。
- **机器人不动**：
  1. `ros2 controller list` 看控制器是否 `active`；
  2. `ros2 topic echo /cmd_vel` 看遥控消息是否在发；
  3. 检查 `wheel_separation` / `wheel_radius` 与 URDF 是否一致。
- **`/scan` 没有数据**：`gz topic -l | grep scan` 看 Gazebo 侧有没有 `/scan`；
  检查 bridge.yaml 与 URDF 里 `<topic>scan</topic>` 是否一致。
- **RViz 里 TF 报过去时间错误（extrapolation）**：所有节点 `use_sim_time` 必须全为 true。
- **改控制器 YAML 不生效**：YAML 安装在 share 目录，改完要 `colcon build` 再重启仿真。

## 6. 下一课

[../08-rviz-visualization](../08-rviz-visualization/)：学会 Marker 和点云可视化，为调试导航做准备。
