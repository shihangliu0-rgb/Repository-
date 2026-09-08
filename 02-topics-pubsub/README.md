# 第 02 课 · 话题：发布 / 订阅

> **目标**：掌握 ROS 2 最核心的通信方式——**话题（Topic）**。一个节点发布、任意多个节点订阅，
> 单向、异步、持续的消息流。

## 1. 本课概念

- **话题**：带名字的单向消息总线，发布者不知道谁在听，订阅者不知道谁在发（解耦）。
- **消息（Message）**：强类型数据结构。本课用 `std_msgs/msg/String`。
- **QoS（服务质量）**：决定消息「怎么传」。入门只需知道两个：
  - `depth`：发送端缓存多少条未送达消息（本课用 10）；
  - `reliability`：`reliable`（尽量送达）或 `best_effort`（尽力，低延迟）。默认 `reliable`。
- **DDS**：ROS 2 底层通信中间件，节点自动发现彼此，无需主节点（没有 roscore！）。

```
  talker ──publish──►  /chatter  ──subscribe──► listener
              (std_msgs/msg/String, 1 Hz)
```

## 2. 编译与运行

```bash
cd 02-topics-pubsub
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

**终端 1（发布者）**：

```bash
ros2 run talker_listener talker
```

**终端 2（订阅者）**：

```bash
ros2 run talker_listener listener
```

预期：talker 打印 `发布: Hello from talker #N`，listener 打印 `收到: Hello from talker #N`。

> C++ 版本同样编译好了：`ros2 run talker_listener_cpp talker` / `listener`。
> 可以 Python talker 配 C++ listener 混跑——这正是「消息类型即接口」的威力。

## 3. `ros2 topic` 全家桶（重点练习）

另开终端（记得 source），边跑边敲：

```bash
ros2 topic list                     # 列出所有话题
ros2 topic list -t                  # 附带消息类型
ros2 topic info /chatter            # 发布者/订阅者数量与 QoS
ros2 topic echo /chatter            # 实时打印消息内容
ros2 topic hz /chatter              # 测量发布频率（应约 1 Hz）
ros2 topic type /chatter            # 查看消息类型
ros2 interface show std_msgs/msg/String   # 查看消息结构定义

# 你也可以当一个发布者（向 /chatter 注入消息，listener 会同时收到两路消息）
ros2 topic pub -r 2 /chatter std_msgs/msg/String "{data: '来自命令行的消息'}"
```

## 4. 作业

1. 把发布频率改成 5 Hz，用 `ros2 topic hz` 验证。
2. 新建 `topic_monitor` 节点：订阅 `/chatter`，统计 10 秒内收到的消息条数并打印（提示：再加一个定时器）。
3. 启动两个 listener，观察同一个话题被多个订阅者接收；再启动两个 talker，观察 listener 同时收到两路消息。
4. （挑战）把消息类型换成 `std_msgs/msg/Int32`，发布自增整数，观察需要改动哪些地方。

## 5. 常见问题

- **listener 收不到消息**：确认两个终端都 `source` 了；`ros2 topic info /chatter` 看两端是否都注册上。
- **`ros2 topic echo` 没有输出**：发布端是否在运行？话题名是否一致（注意前导 `/`）？

## 6. 下一课

[../03-services-actions](../03-services-actions/)：需要「一问一答」时，用服务；需要「长任务+进度」时，用 Action。
