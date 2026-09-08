# 第 03 课 · 服务与 Action

> **目标**：掌握另外两种通信范式——**服务（Service）**：一问一答；**Action**：长任务 + 实时反馈 + 最终结果。

## 1. 三种通信方式怎么选？

| 方式 | 特点 | 典型场景 |
|------|------|----------|
| 话题 | 单向、持续流、多对多 | 传感器数据、状态广播 |
| 服务 | 请求→应答，一次完成 | 开关使能、查询、参数设置 |
| Action | 目标→反馈流→结果，可取消 | 导航到某点、机械臂运动到某位姿 |

本课示例全部使用官方内置接口包 `example_interfaces`（加法服务、Fibonacci Action），
第 04 课我们会定义自己的接口。

## 2. 编译

```bash
cd 03-services-actions
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

## 3. 服务：两数相加

**终端 1（服务端）**：

```bash
ros2 run service_demo add_two_ints_server
```

**终端 2（客户端）**：

```bash
ros2 run service_demo add_two_ints_client          # 默认 41 + 1
ros2 run service_demo add_two_ints_client 3 4      # 自定义两个整数
```

也可以不写代码，直接用命令行当客户端：

```bash
ros2 service list                                   # 应能看到 /add_two_ints
ros2 service type /add_two_ints                     # example_interfaces/srv/AddTwoInts
ros2 interface show example_interfaces/srv/AddTwoInts
ros2 service call /add_two_ints example_interfaces/srv/AddTwoInts "{a: 7, b: 8}"
```

## 4. Action：Fibonacci 数列（带进度反馈）

**终端 1（Action 服务端）**：

```bash
ros2 run service_demo fibonacci_action_server
```

**终端 2（Action 客户端）**：

```bash
ros2 run service_demo fibonacci_action_client        # 请求 10 个数
```

预期：客户端先逐条打印 `反馈: [0, 1, 1, ...]`，最后打印 `结果: [...]`。

命令行方式：

```bash
ros2 action list                                   # /fibonacci
ros2 action info /fibonacci -t                     # example_interfaces/action/Fibonacci
ros2 action send_goal /fibonacci example_interfaces/action/Fibonacci "{order: 8}" --feedback
```

> 注意 `--feedback`：你能实时看到进度——这正是 Action 相比服务的核心价值。

## 5. 作业

1. 给加法服务端加校验：输入为负数时返回失败（需要换接口吗？想想为什么 `AddTwoInts` 做不到，引出第 04 课）。
2. 修改 Fibonacci 客户端，把 `order` 改成从命令行参数读取。
3. （挑战）写一个 `SleepActionServer`：目标为秒数，反馈为已睡秒数，结果为“睡醒啦”。提示：自定义 action 在第 04 课学。

## 6. 常见问题

- **客户端卡在等待响应**：服务端没起 / 服务名不一致。`ros2 service list` 检查。
- **Action 收不到反馈**：确认用了 `--feedback` 参数，且服务端在 `execute` 里调用了 `publish_feedback`。

## 7. 下一课

[../04-custom-interfaces](../04-custom-interfaces/)：内置接口不够用？自己定义 msg / srv / action。
