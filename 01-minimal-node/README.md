# 第 01 课 · 最小节点

> **目标**：理解「节点（Node）」这个 ROS 2 最小执行单元，跑通 *编写 → 编译 → 运行 → 观察* 全流程。

## 1. 本课概念

- **节点（Node）**：一个独立的可执行程序，是 ROS 2 计算图的基本单元。一个机器人系统由几十上百个节点组成（感知、决策、控制……各司其职）。
- **工作空间（Workspace）**：一个目录，里面 `src/` 放源码包，编译后生成 `build/ install/ log/`。
- **功能包（Package）**：ROS 2 的代码组织单元。本课有两个：
  - `minimal_node`：Python 版（`ament_python` 构建）
  - `minimal_node_cpp`：C++ 版（`ament_cmake` 构建）
- **spin**：让节点「活着」的事件循环；`create_timer` 周期性回调就是节点的心跳。

## 2. 目录结构（学习重点）

```
01-minimal-node/
└── src/
    ├── minimal_node/                 ← Python 包
    │   ├── package.xml               ← 包的身份证：名字、依赖
    │   ├── setup.py                  ← 安装规则：哪个函数注册成哪个可执行文件
    │   ├── setup.cfg                 ← 固定写法
    │   ├── resource/minimal_node     ← ament 索引标记文件（空文件即可）
    │   └── minimal_node/
    │       ├── __init__.py
    │       └── hello_node.py         ← 节点源码
    └── minimal_node_cpp/             ← C++ 包
        ├── package.xml
        ├── CMakeLists.txt            ← 编译规则
        └── src/hello_node.cpp        ← 节点源码
```

## 3. 编译

```bash
cd 01-minimal-node
rosdep install --from-paths src --ignore-src -r -y   # 首次：安装依赖
colcon build --symlink-install
source install/setup.bash
```

> 每个**新终端**都要重新 `source install/setup.bash`。

## 4. 运行

```bash
# Python 版
ros2 run minimal_node hello_node
# C++ 版
ros2 run minimal_node_cpp hello_node
```

预期输出（每秒一条）：

```
[INFO] [hello_node]: HelloNode 启动！
[INFO] [hello_node]: Hello ROS 2! 心跳 #1 (节点名: hello_node, 命名空间: /)
[INFO] [hello_node]: Hello ROS 2! 心跳 #2 (节点名: hello_node, 命名空间: /)
```

`Ctrl+C` 退出，观察优雅退出的日志。

## 5. 命令行观察（另开终端，记得 source）

```bash
ros2 node list                 # 列出所有在线节点
ros2 node info /hello_node     # 查看节点的订阅/发布/服务/参数
```

## 6. 作业

1. 把心跳周期从 1 秒改成 0.2 秒，并把日志内容改成你的名字。
2. 给节点换一个名字（构造函数里 `super().__init__('...')`），重新编译观察 `ros2 node list`。
3. （C++）修改 `hello_node.cpp`，只在心跳数为 10 的倍数时打印日志，重新编译运行验证。

## 7. 常见问题

- **`No package named 'minimal_node' found`**：没 `source install/setup.bash`。
- **colcon 报 `colcon: command not found`**：`sudo apt install python3-colcon-common-extensions`。

## 8. 下一课

[../02-topics-pubsub](../02-topics-pubsub/)：让两个节点通过**话题**互相说话。
