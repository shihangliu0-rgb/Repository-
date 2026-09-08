# 第 05 课 · Launch 与参数

> **目标**：用一条命令拉起一组节点，并用「参数」灵活配置它们。
> 真实机器人动辄几十个节点，没有人会一个个 `ros2 run`。

## 1. 本课概念

- **参数（Parameter）**：节点的配置项（字符串/数字/布尔/数组），可在启动时给定、运行时修改。
- **Launch 文件**：Python 脚本，描述「要启动哪些节点、用什么参数、话题怎么重命名」。
- 本课 4 个 launch 文件由浅入深：
  1. `two_nodes.launch.py` —— 最基础：启动两个节点
  2. `with_args.launch.py` —— 启动参数：`ros2 launch` 时传值
  3. `with_yaml.launch.py` —— 用 YAML 文件集中管理参数
  4. `advanced.launch.py` —— 话题重映射 + 命名空间 + include 组合

## 2. 编译

```bash
cd 05-launch-parameters
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

## 3. 逐个运行

### ① 基础版

```bash
ros2 launch launch_demo two_nodes.launch.py
```

talker 以默认参数发布，listener 打印。`Ctrl+C` 一次退出所有节点。

### ② 启动参数（命令行传值）

```bash
ros2 launch launch_demo with_args.launch.py message:="我是从命令行传入的" frequency:=3.0
ros2 launch launch_demo with_args.launch.py --show-args    # 查看支持哪些参数
```

### ③ YAML 参数文件

```bash
ros2 launch launch_demo with_yaml.launch.py
```

参数全部来自 `config/talker_params.yaml` —— 学会看这个文件的结构（节点名 → `ros__parameters`）。

### ④ 高级：重映射 + 命名空间 + include

```bash
ros2 launch launch_demo advanced.launch.py
```

这个文件演示了三件事：

- **GroupAction + PushRosNamespace**：把一组节点塞进 `/demo` 命名空间（话题变成 `/demo/chatter`）；
- **remappings**：把 talker 的 `chatter` 重命名成 `news`；
- **IncludeLaunchDescription**：在 launch 里再 include 另一个 launch（`two_nodes.launch.py`）。

验证：另开终端 `ros2 topic list`，应同时看到 `/demo/news`、`/chatter` 等。

## 4. 参数命令行练习

```bash
ros2 launch launch_demo two_nodes.launch.py          # 保持运行

# 另开终端：
ros2 param list /talker                    # 列出参数
ros2 param get /talker message             # 读取
ros2 param set /talker message "改啦！"     # 动态修改（talker 立即生效，观察日志）
ros2 param dump /talker                    # 导出全部参数（可直接存成 YAML 复用）
```

> 「运行时改参数立即生效」是怎么做到的？看 `talker.py` 里的
> `add_on_set_parameters_callback` —— 这是参数热更新的标准写法。

## 5. 作业

1. 给 `with_args.launch.py` 增加第三个启动参数 `prefix`，传给 listener。
2. 复制 `talker_params.yaml` 改一份 `fast_params.yaml`（频率 5Hz），让 launch 文件通过**启动参数**选择用哪个 YAML。
3. （挑战）写一个 `shutdown_demo.launch.py`：当 listener 退出时自动关闭整个 launch。
   提示：`launch.actions.RegisterEventHandler` + `OnProcessExit` + `Shutdown`。

## 6. 常见问题

- **`parameter 'xxx' has invalid type`**：YAML 里数字不要加引号；启动参数传的都是字符串，节点声明类型要匹配（`frequency` 声明为 `double`，launch 会自动转换）。
- **改了 launch 文件不生效**：launch 目录是安装到 `install/` 的，`--symlink-install` 下改 `.launch.py` 是即时生效的，但**新增**文件要重新 `colcon build`。

## 7. 下一课

[../06-urdf-rviz](../06-urdf-rviz/)：编程基础篇结束！开始造机器人——URDF 建模与 RViz 可视化。
