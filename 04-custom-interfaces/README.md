# 第 04 课 · 自定义接口（msg / srv / action）

> **目标**：定义自己的消息、服务和 Action 接口，并在真实节点里使用。
> 这是机器人项目里出现频率最高的操作之一——你的传感器、你的协议，就该有自己的接口。

## 1. 接口定义语法速查

**msg**（消息，用 `#` 注释）：

```
# StudentInfo.msg
string name
uint8 age
float32 score
```

**srv**（服务，`---` 分隔请求与应答）：

```
# SetSpeed.srv
float64 linear_x
float64 angular_z
---
bool success
string message
```

**action**（三段：目标 `---` 结果 `---` 反馈）：

```
# Charge.action
int32 dock_id
---
bool success
float32 battery_level
---
float32 progress
```

支持的字段类型：`bool byte char int8~64 uint8~64 float32/64 string`、数组（`float64[]`）、
嵌套（`geometry_msgs/Pose`）、常量（`int32 MAX=10`）。

## 2. 本课两个包的关系（重点理解）

```
custom_interfaces   ← 接口包（ament_cmake + rosidl 生成器，只负责生成代码）
        ▲ 依赖
        │
interface_demo      ← 使用接口的节点（Python）
```

接口包必须在 `package.xml` 里声明三件套：

```xml
<buildtool_depend>rosidl_default_generators</buildtool_depend>
<exec_depend>rosidl_default_runtime</exec_depend>
<member_of_group>rosidl_interface_packages</member_of_group>
```

`colcon` 会按依赖关系**自动先编译接口包**，再编译使用它的包。

## 3. 编译

```bash
cd 04-custom-interfaces
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

## 4. 运行

**终端 1**：发布自定义消息 `StudentInfo`

```bash
ros2 run interface_demo student_publisher
```

**终端 2**：观察

```bash
ros2 interface show custom_interfaces/msg/StudentInfo
ros2 topic echo /student_info
```

**终端 1 保持运行**，**终端 3**：启动自定义服务 `SetSpeed`

```bash
ros2 run interface_demo speed_server
```

**终端 4**：调用（两种写法都行）

```bash
# 命令行调用
ros2 service call /set_speed custom_interfaces/srv/SetSpeed \
  "{linear_x: 0.5, angular_z: 0.3}"

# 或运行示例客户端
ros2 run interface_demo speed_client 0.2 0.1
```

## 5. 作业

1. 给 `StudentInfo` 增加一个 `string[] courses` 字段（选课列表），修改 `student_publisher` 并验证。
2. 让 `SetSpeed` 服务拒绝非法速度（|linear_x| > 1.0 时返回 `success: false` 并给出原因）。
3. （挑战）为 `Charge.action` 写一个 Action 服务端：反馈里 `progress` 从 0 涨到 1，结果返回 `battery_level`。

## 6. 常见问题

- **`Could not find the interface 'custom_interfaces/msg/StudentInfo'`**：
  接口包没编译成功或没 source。先看 `colcon build` 是否全绿。
- **改了 .msg 没生效**：接口代码是编译期生成的，必须重新 `colcon build`（`--symlink-install` 不覆盖生成代码）。

## 7. 下一课

[../05-launch-parameters](../05-launch-parameters/)：一条命令拉起一群节点 —— Launch 文件与参数。
