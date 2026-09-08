# 环境安装与常见问题

本仓库面向 **Ubuntu 24.04 + ROS 2 Jazzy（LTS，支持到 2029）**。
如果你的机器是双系统/虚拟机/WSL2，任选其一，推荐原生或虚拟机（Gazebo 图形界面最稳）。

---

## 1. 安装 ROS 2 Jazzy（desktop 全家桶）

按官方源安装（[官方教程原文](https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html)）：

```bash
# 1) 确保 locale 是 UTF-8
sudo apt update && sudo apt install locales
sudo locale-gen en_US en_US.UTF-8
sudo update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8

# 2) 添加 ROS 2 apt 源
sudo apt install software-properties-common
sudo add-apt-repository universe
sudo apt update && sudo apt install curl -y
sudo curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
  http://packages.ros.org/ros2/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" | \
  sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null

# 3) 安装 desktop 全家桶（含 rviz2、仿真工具、demo）
sudo apt update
sudo apt upgrade -y
sudo apt install ros-jazzy-desktop -y

# 4) 开发工具：colcon 构建器 + rosdep 依赖管理
sudo apt install python3-colcon-common-extensions python3-rosdep python3-argcomplete -y
sudo rosdep init || true     # 已初始化会报错，忽略即可
rosdep update
```

把环境加载写进 `~/.bashrc`（每个新终端自动生效）：

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

### 验证安装

```bash
# 终端 1
ros2 run demo_nodes_cpp talker
# 终端 2
ros2 run demo_nodes_py listener
# 看到 "I heard: [Hello World: N]" 即安装成功
```

图形界面验证：

```bash
rviz2          # 能弹出窗口即 RViz 正常
gz sim -r      # 能弹出 Gazebo 并看到一个摆/小车即仿真正常（首次启动较慢）
```

---

## 2. 每课的依赖安装

每课工作空间的 `src/` 里所有 `package.xml` 都声明了依赖，统一用 `rosdep` 一键安装：

```bash
cd <课程目录>          # 例如 07-gazebo-sim
rosdep install --from-paths src --ignore-src -r -y
```

主要课程额外用到的系统包（rosdep 都会覆盖，这里列出便于排错）：

| 课程 | 关键依赖 |
|------|----------|
| 01–02（C++ 部分） | `ros-jazzy-rclcpp`、`build-essential` |
| 06 | `ros-jazzy-xacro`、`ros-jazzy-joint-state-publisher-gui`、`ros-jazzy-robot-state-publisher` |
| 07–10 | `ros-jazzy-ros-gz`（桥接+仿真）、`ros-jazzy-gz-ros2-control`、`ros-jazzy-ros2-controllers` |
| 09 | `ros-jazzy-slam-toolbox`、`ros-jazzy-nav2-map-server` |
| 10 | `ros-jazzy-navigation2`、`ros-jazzy-nav2-bringup` |

---

## 3. 编译工作空间（通用流程）

```bash
cd <课程目录>
colcon build --symlink-install    # --symlink-install：改 Python 源码不用重新编译
source install/setup.bash         # 每个新终端都要执行（或写进 ~/.bashrc）
```

建议给每个终端都执行 `source`，也可以：

```bash
echo "source ~/path/to/<课程目录>/install/setup.bash" >> ~/.bashrc
```

---

## 4. 常见问题（FAQ）

**Q1：`ros2: command not found`**
没 `source /opt/ros/jazzy/setup.bash`。检查第 1 步第 4 条是否写进了 `~/.bashrc`。

**Q2：`colcon build` 报 `Could not find a package configuration file provided by "xxx"`**
缺依赖。先 `source /opt/ros/jazzy/setup.bash`，再 `rosdep install --from-paths src --ignore-src -r -y`。

**Q3：编译成功但 `ros2 run` 找不到包**
忘了 `source install/setup.bash`。注意：先 source 系统环境，再 source 工作空间。

**Q4：Gazebo 打开黑屏/白屏**
- 虚拟机：3D 加速开启，显存给到 128MB+；
- 试试 `export LIBGL_ALWAYS_SOFTWARE=1` 后再启动；
- 首次启动要下载渲染资源，耐心等待 1~2 分钟。

**Q5：RViz 里提示 `Fixed Frame [map] does not exist`**
TF 树还没建立或没连上：确认所有节点 `use_sim_time` 一致（仿真里全为 true），
`ros2 topic hz /clock` 应该有数据。

**Q6：话题没人收到消息**
常见于 QoS 不匹配（例如一方 transient_local 一方 volatile）。本仓库所有示例都用默认
QoS，若你自行修改过，先用 `ros2 topic info <话题> --verbose` 对比两端 QoS。

**Q7：WSL2 里没有图形界面**
安装 WSLg（Windows 11 自带）或用 VcXsrv；Gazebo 在 WSL2 中性能一般，建议虚拟机/双系统。

**Q8：`gz sim` 和 `gazebo` 是什么关系？**
Jazzy 配套的仿真器是新版 **Gazebo（原 Ignition，Harmonic 版本）**，命令是 `gz sim`；
老教程里的 `gazebo` 是 Gazebo Classic（已于 2025 年停止维护）。本仓库统一使用新版。

**Q9：中文输入法终端下命令粘贴乱码**
用英文输入法粘贴命令，或手动输入关键字符（引号、冒号必须是英文半角）。

---

## 5. 建议的目录习惯

```
~/ros2-learn/
├── Repository-/              ← 本仓库（直接 git clone）
│   ├── 01-minimal-node/      ← 每课一个工作空间，独立编译
│   └── ...
```

每课学完后可以 `git commit` 记录自己的修改，方便对照回退。
