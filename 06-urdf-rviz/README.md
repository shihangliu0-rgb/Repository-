# 第 06 课 · URDF 建模 + RViz 可视化

> **目标**：用 URDF（xacro）从零描述一台两轮差速机器人，并在 RViz 里可视化、拖动关节。
> 这个模型就是后面仿真、SLAM、导航用的同一台机器人。

## 1. 本课概念

- **URDF**：用 XML 描述机器人的**连杆（link）**和**关节（joint）**的树状结构。
  - `link`：一段刚体，含外观 `visual`、碰撞体 `collision`、惯量 `inertial`。
  - `joint`：连接两个 link，类型有 `fixed / revolute / continuous / prismatic`。
- **xacro**：URDF 的「宏语言」。用 `property` 存参数、`macro` 复用结构，避免大段复制粘贴。
- **robot_state_publisher**：读 `/robot_description`（URDF）+ `/joint_states`（关节角），
  发布整棵 **TF 树**——所有可视化与定位都靠它。
- **joint_state_publisher_gui**：提供滑块，手动给关节角，方便在没有真实/仿真数据时检查模型。

```
base_footprint ─ base_link ─┬─ left_wheel   (continuous, 会转)
                            ├─ right_wheel  (continuous, 会转)
                            ├─ caster_wheel (fixed, 球)
                            └─ lidar_link   (fixed)
```

## 2. 编译与运行

```bash
cd 06-urdf-rviz
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash

ros2 launch robot_description display.launch.py
```

RViz 里会看到蓝色底盘、两个黑轮、红色雷达；`joint_state_publisher_gui` 窗口里拖动
`left_wheel_joint / right_wheel_joint` 滑块，轮子跟着转。

## 3. 动手练习（重点）

1. **检查 URDF 是否合法**：
   ```bash
   xacro src/robot_description/urdf/robot.urdf.xacro        # 看展开后的完整 URDF
   ros2 run xacro xacro src/robot_description/urdf/robot.urdf.xacro > /tmp/robot.urdf
   check_urdf /tmp/robot.urdf                                # 打印连杆树
   ```
2. **看 TF 树**：另开终端
   ```bash
   ros2 run tf2_tools view_frames        # 生成 frames.pdf
   ros2 run tf2_ros tf2_echo base_footprint lidar_link   # 实时打印两坐标系的变换
   ```
3. **改尺寸**：把 `robot.urdf.xacro` 顶部 `chassis_width` 从 0.20 改成 0.30，重新编译观察变化。

## 4. 作业

1. 给机器人加一根朝前的「天线」（细长圆柱 + 小球）。
2. 把两个驱动轮改成 `revolute` 并加上 `<limit>`（转角范围），观察 GUI 滑块的变化。
3. （挑战）用 `xacro:macro` 把「轮子」改成可以传入半径的通用宏，做一个可配置轮径的模型。

## 5. 常见问题

- **RViz 里模型是白的/报错 `no tf data`**：确认 `robot_state_publisher` 在运行，且 Fixed Frame 选的是存在的坐标系（`base_footprint`）。
- **xacro 报 `unknown macro`**：宏名拼写，或 `xacro:wheel ...` 调用在宏定义之前（xacro 要求先定义后使用）。
- **轮子悬空/陷进地面**：检查 `base_joint` 的 z 偏移与轮半径是否匹配。

## 6. 下一课

[../07-gazebo-sim](../07-gazebo-sim/)：把这台机器人放进 Gazebo 物理仿真，用键盘遥控它。
