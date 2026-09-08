# ROS 2 实战学习仓库 —— 从零到仿真导航

> 一个可以**从头敲到尾**的 ROS 2 学习路线：10 个独立工作空间，每课都是完整可编译的代码，
> `colcon build` → `source` → `ros2 launch`，一路从「最小节点」走到 **Gazebo 仿真 + SLAM 建图 + Nav2 导航**。

目标发行版：**ROS 2 Jazzy（Ubuntu 24.04）**。详细环境安装见 [docs/setup.md](docs/setup.md)，
完整学习计划（每课目标/知识点/验收标准）见 [PLAN.md](PLAN.md)。

---

## 课程总览

| 课 | 目录 | 主题 | 你将得到 |
|----|------|------|----------|
| 01 | [01-minimal-node](01-minimal-node/) | 最小节点 | 第一个会打印心跳的节点（Python + C++） |
| 02 | [02-topics-pubsub](02-topics-pubsub/) | 话题：发布/订阅 | talker 与 listener，掌握 `ros2 topic` 全家桶 |
| 03 | [03-services-actions](03-services-actions/) | 服务与 Action | 加法服务、Fibonacci Action（含反馈） |
| 04 | [04-custom-interfaces](04-custom-interfaces/) | 自定义接口 | 自己的 msg / srv / action 并投入使用 |
| 05 | [05-launch-parameters](05-launch-parameters/) | Launch 与参数 | 参数、YAML、启动参数、remap、include 组合 |
| 06 | [06-urdf-rviz](06-urdf-rviz/) | URDF 建模 + RViz | 手写差速机器人模型，RViz 里看它、拖动关节 |
| 07 | [07-gazebo-sim](07-gazebo-sim/) | Gazebo 仿真 | 机器人进仿真世界：ros2_control 驱动 + 激光雷达 + 键盘遥控 |
| 08 | [08-rviz-visualization](08-rviz-visualization/) | RViz 高级可视化 | Marker、点云发布与可视化 |
| 09 | [09-slam-mapping](09-slam-mapping/) | SLAM 建图 | 遥控建图（slam_toolbox）+ 保存地图 |
| 10 | [10-nav2-navigation](10-nav2-navigation/) | Nav2 导航 | 载入地图，AMCL 定位，发送目标点自主导航 |

> 09/10 课的工作空间**自带**仿真所需的全部包（机器人描述 + Gazebo 启动），
> 因此每课都可以独立编译、独立运行，互不依赖。

---

## 快速开始（每课通用三步）

```bash
# 0. 一次性：安装 ROS 2 Jazzy（见 docs/setup.md）
#    并给某课安装依赖（以第 07 课为例）
cd 07-gazebo-sim
rosdep install --from-paths src --ignore-src -r -y   # 自动装齐 package.xml 里的依赖

# 1. 编译
colcon build --symlink-install

# 2. 运行（每个新终端都要先 source）
source install/setup.bash
ros2 launch <包名> <启动文件>     # 具体命令看各课 README
```

每课 `README.md` 的结构都一样：**概念 → 编译 → 运行 → 观察 → 命令行练习 → 作业**。

---

## 仓库结构

```
.
├── README.md               ← 你在这里
├── PLAN.md                 ← 完整学习计划（建议先读）
├── docs/
│   └── setup.md            ← Ubuntu 24.04 + ROS 2 Jazzy 环境安装 & 常见坑
├── scripts/
│   └── check_repo.py       ← 仓库自检（无需 ROS：语法/格式/包结构体检）
├── 01-minimal-node/        ← 每课一个独立工作空间（内含 src/ 与 README）
│   ├── README.md
│   └── src/<功能包>/...
├── ...
└── 10-nav2-navigation/
```

> 编译前可以先跑一把自检：`python3 scripts/check_repo.py`（无需安装 ROS）。

## 学习建议

1. **按顺序学**：前 5 课是编程基础，后 5 课是机器人仿真，层层递进。
2. **每课都动手改代码**：每课 README 末尾的「作业」是刻意设计的，改坏了没关系，`git` 会救你。
3. **遇到问题**：先看当课 README 的「常见问题」，再看 [docs/setup.md](docs/setup.md) 的排错章节。
4. **跑通第 10 课**后，你就具备了：看懂真实机器人项目结构、写驱动上层逻辑、做建图与导航的完整能力。

## 版本说明

- 本仓库所有代码面向 **ROS 2 Jazzy + Gazebo (Harmonic)**（2024–2029 LTS 组合）。
- 若你使用 Humble：Python/C++ 课（01–05）代码完全通用；06–10 课需把 `gz` 相关包换成
  `ign`/Gazebo Classic 对应物，不建议初学者折腾，直接装 Jazzy 最省事。
