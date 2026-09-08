# ROS 2 学习计划（从零到仿真导航）

本计划按「**每课一个独立工作空间、学完一课验收一课**」设计。建议总学时 20~30 小时，
可按每天 1~2 小时安排。每课目录内的 `README.md` 是操作手册，本文件是学习地图。

```
学习路线：

 最小节点 ──► 话题(发布/订阅) ──► 服务/Action ──► 自定义接口 ──► Launch/参数
    01              02                 03               04              05
                                                                        │
 导航(自主移动) ◄── SLAM建图 ◄── RViz可视化 ◄── Gazebo仿真 ◄── URDF建模 │
     10              09             08             07           06 ◄────┘
```

---

## 阶段一：ROS 2 编程基础（第 01–05 课）

### 第 01 课 · 最小节点（01-minimal-node）
- **目标**：理解「节点（Node）」这个最小执行单元，跑通编译全流程。
- **知识点**：工作空间/功能包目录结构、`rclpy` 生命周期、`spin`、日志系统、`ros2 node` CLI。
- **任务**：编译并以两种方式运行心跳节点；用 `ros2 node list / info` 观察。
- **验收**：终端每秒打印一条心跳日志；`ros2 node info /hello_node` 能看到节点。
- **预计时间**：1~1.5 小时。

### 第 02 课 · 话题发布/订阅（02-topics-pubsub）
- **目标**：掌握 ROS 2 最核心的通信方式——话题（Topic）。
- **知识点**：Publisher/Subscriber、消息类型、QoS 入门（深度/可靠性）、`ros2 topic` CLI。
- **任务**：运行 talker/listener（Python 与 C++ 双版本）；手动 `ros2 topic pub` 注入消息。
- **验收**：`ros2 topic echo /chatter` 能看到消息流；`ros2 topic hz` 频率约 1Hz。
- **预计时间**：1.5~2 小时。

### 第 03 课 · 服务与 Action（03-services-actions）
- **目标**：掌握「请求-应答」的服务与「长任务+反馈」的 Action。
- **知识点**：Service 同步语义、Action 的 goal/feedback/result 三要素、与话题的选型对比。
- **任务**：运行加法服务器/客户端、Fibonacci Action 服务器/客户端；用命令行调用它们。
- **验收**：`ros2 service call` 得到加法结果；Action 客户端逐条打印进度反馈后收到结果。
- **预计时间**：2~3 小时。

### 第 04 课 · 自定义接口（04-custom-interfaces）
- **目标**：定义自己的 msg / srv / action，并在节点中使用。
- **知识点**：`rosidl_generate_interfaces`、接口包与普通包的依赖关系、`ros2 interface show`。
- **任务**：编译接口包；运行发布 `StudentInfo` 消息的节点与提供 `SetSpeed` 服务的节点。
- **验收**：`ros2 topic echo /student_info` 看到自定义消息；`ros2 service call` 用自定义服务成功。
- **预计时间**：1.5~2 小时。

### 第 05 课 · Launch 与参数（05-launch-parameters）
- **目标**：用 launch 文件一键拉起多个节点，用参数配置行为。
- **知识点**：`LaunchDescription`、`DeclareLaunchArgument`、参数声明/动态修改、YAML 参数文件、话题重映射、include 组合。
- **任务**：依次运行 4 个渐进式 launch 文件；运行时用 `ros2 param set` 动态改发布内容。
- **验收**：`ros2 launch <包> 02_with_args.launch.py message:="自定义内容"` 生效。
- **预计时间**：2~3 小时。

---

## 阶段二：机器人建模与仿真（第 06–08 课）

### 第 06 课 · URDF 建模 + RViz（06-urdf-rviz）
- **目标**：用 URDF/xacro 从零描述一台两轮差速机器人，并在 RViz 中可视化。
- **知识点**：link/joint/inertia、xacro 宏与参数化、`robot_state_publisher`、`joint_state_publisher_gui`、TF 基础。
- **任务**：启动 display.launch.py，用 GUI 滑块转动轮子；用 `tf2_tools` 导出 TF 树。
- **验收**：RViz 中机器人模型完整显示，拖动滑块轮子跟着转，TF 树无断裂。
- **预计时间**：2~3 小时。

### 第 07 课 · Gazebo 仿真（07-gazebo-sim）
- **目标**：让机器人进入物理仿真世界，能遥控它跑起来并读到激光雷达。
- **知识点**：Gazebo (Harmonic) 世界文件、`ros_gz` 桥接、`ros2_control` + `diff_drive_controller`、gpu_lidar 传感器、`use_sim_time`。
- **任务**：一条 launch 拉起「世界 + 机器人 + 控制器 + 桥接」；第二终端键盘遥控。
- **验收**：键盘能驱动机器人；`ros2 topic echo /scan` 有雷达数据；`/odom` 与 `odom→base_link` TF 正常。
- **预计时间**：3~4 小时。

### 第 08 课 · RViz 高级可视化（08-rviz-visualization）
- **目标**：学会向 RViz 发布 Marker 与点云，这是调试感知/规划结果的必备技能。
- **知识点**：`visualization_msgs/Marker(Array)` 各类型、`PointCloud2` 内存布局、RViz 配置文件(.rviz)。
- **任务**：运行 marker 演示与点云演示；向工程里加入自己的可视化。
- **验收**：RViz 中看到旋转立方体、球环、文字与波浪点云。
- **预计时间**：1.5~2 小时。

---

## 阶段三：建图与导航（第 09–10 课）

### 第 09 课 · SLAM 建图（09-slam-mapping）
- **目标**：在仿真里边遥控边建图（slam_toolbox），并保存地图文件。
- **知识点**：SLAM 原理概览（里程计+激光匹配）、slam_toolbox 参数（分辨率/帧/模式）、`map_saver`、地图文件格式（pgm+yaml）。
- **任务**：启动「仿真 + SLAM + RViz」，遥控机器人走遍地图每个角落，保存地图。
- **验收**：RViz 的 `/map` 随行驶实时生长；得到 `my_map.yaml + my_map.pgm`。
- **预计时间**：2~3 小时。

### 第 10 课 · Nav2 导航（10-nav2-navigation）
- **目标**：在已知地图上实现「给个目标点，机器人自己开过去」的完整导航。
- **知识点**：AMCL 粒子滤波定位、全局/局部代价地图、规划器与控制器、行为树与恢复行为、Nav2 参数调优。
- **任务**：一条 launch 拉起「仿真 + 地图 + Nav2 + RViz」；标定初始位姿后发送导航目标。
- **验收**：机器人绕开障碍物到达目标点；能解释全局代价地图与局部代价地图的区别。
- **预计时间**：3~5 小时（含调参玩耍时间）。

---

## 结业检验（综合项目）

全部完成后，挑战以下任意一项，检验学习成果：

1. **改造世界**：在 `learning_world.sdf` 里加房间/走廊，重新建图并导航。
2. **换底盘**：把两轮差速改成三轮全向（omni），修改控制器与导航参数。
3. **加点智能**：写一个节点，监听 `/scan`，前方 0.3m 内有障碍就强制停车（安全卫士）。
4. **巡航模式**：用 Nav2 的 waypoint follower 让机器人按路径点巡逻。

## 继续进阶方向

- **MoveIt 2**：机械臂运动规划（另一条主线）。
- **ros2_control 真机**：把仿真里的控制器配置直接用于真实硬件接口。
- **Nav2 深度**：行为树自定义、costmap filter（限速区/禁区）、MPPI 控制器。
- **micro-ROS**：把 ROS 2 带到 STM32/ESP32 单片机。
- **工程化**：`colcon test`、`ros2 bag` 录制回放、Docker、CI。

## 参考资料

- ROS 2 官方文档（中文友好）：<https://docs.ros.org/en/jazzy/>
- Nav2 文档：<https://docs.nav2.org/>
- Gazebo 教程：<https://gazebosim.org/docs/harmonic/>
- ros2_control 文档：<https://control.ros.org/jazzy/>
- The Construct / Articulated Robotics 的配套视频（搜索对应课程名）
