# Windows 程序运行原理 + 游戏逆向分析 · 学习仓库

这个仓库是你（学习者）的**实验台**，不是一个成品修改器。
最终实验对象是你自己拥有的单机游戏《英雄连 / Company of Heroes》。
前面 4 个阶段全部用你自己写的小 C 程序当小白鼠——因为它们足够小，出了问题你能看懂。

---

## 目录结构

```
Repository-/
├── README.md                ← 你在这里
├── lessons/                 ← 每节课的讲义（严格按固定 8 段格式写）
│   ├── 01-windows-exe.md
│   └── 02-process-virtual-memory.md
├── labs/                    ← 你要亲手编译、运行、观察的小程序
│   ├── lab01/
│   │   ├── lab01.c          ← 主实验：int money = 100; 死循环
│   │   ├── lab01b.c         ← 对照组：全局 / 栈 / 堆 三种变量
│   │   └── build_lab01.bat  ← Windows 一键编译脚本
│   └── lab02/
│       ├── lab02a.c         ← 两个进程抢同一个地址（虚拟地址空间隔离）
│       ├── lab02b.c         ← 一个进程四个线程（各自的栈，共享的全局变量）
│       ├── lab02c.c         ← 堆会长大（Reserved / Committed / WorkingSet）
│       ├── lab02d.c         ← 模块基址 / ASLR / 基址+RVA=真实地址
│       ├── lab02e.c         ← 自己走一遍地址空间（VirtualQueryEx），可查别的 PID
│       └── build_lab02.bat
└── tools/                   ← 只用 Python 标准库的小工具（不装任何东西）
    ├── pe_view.py           ← 把 EXE 当数据看：PE 头、节表、导入 DLL、ASLR 标志
    └── scan_value.py        ← 在文件里搜一个数值（第 6 课搜内存用的是同一套思路）
```

---

## 十二阶段路线图

| 阶段 | 主题 | 主要工具 | 状态 |
|---|---|---|---|
| 1 | Windows EXE 是什么、进程、线程、变量住哪 | cl/g++、任务管理器、`pe_view.py` | 已写 |
| 2 | 虚拟地址空间、页、状态/类型/保护、DLL 加载、Windows API、PID vs HANDLE | System Informer + `labs/lab02/` 五个小程序 | **← 现在这里** |
| 3 | 调试器：断点、单步、寄存器、改内存 | x64dbg | 待写 |
| 4 | 指针、`&`、`*`、多级指针 | 自己写的 C 程序 + x64dbg | 待写 |
| 5 | 游戏里的"数据"到底是什么 | 《英雄连》+ 只观察不修改 | 待写 |
| 6 | 第一次内存搜索 | Cheat Engine（只用扫描功能） | 待写 |
| 7 | 动态地址、模块基址、偏移、指针链、ASLR | x64dbg + CE 的指针扫描 | 待写 |
| 8 | 结构体：对象 = 一段连续内存 | 自己写的 C 程序 | 待写 |
| 9 | 只看懂 9 条汇编指令 | x64dbg 反汇编窗口 | 待写 |
| 10 | 外部修改器原理：OpenProcess / Read / WriteProcessMemory | 自己写的小读取器 | 待写 |
| 11 | DLL、LoadLibrary、导出函数、Hook、代码注入 | 最后才碰 | 待写 |
| 12 | 最终项目：《英雄连》单机状态观察器 v1→v5 | 你自己写 | 待写 |

---

## 需要装的东西（按阶段，用不到就别装）

| 工具 | 什么时候要 | 为什么 | 只用它的哪些功能 |
|---|---|---|---|
| **Visual Studio Build Tools**（勾选"使用 C++ 的桌面开发"）<br>或 **MSYS2 / w64devkit** 里的 g++ | 第 1 课就要 | 你要自己编译实验程序；MSVC 还自带 `dumpbin` 反汇编器 | `cl.exe` 编译、`dumpbin /headers /disasm /imports` |
| **Python 3.x**（Windows 版，装的时候勾 "Add to PATH"） | 第 1 课就要 | 跑本仓库 `tools/` 里的只读观察脚本 | 命令行 `python xxx.py` |
| **任务管理器** | 第 1 课 | Windows 自带，看进程/PID/内存 | 详细信息页 + 列自定义 |
| **System Informer**（原 Process Hacker 的官方续作，开源免费） | **第 2 课就要** | 任务管理器只给汇总数字，看不到地址空间内部长什么样 | 只用进程属性里的 **Threads / Modules / Memory** 三页 + Memory 页双击看十六进制。内核驱动**不用装**。网络/磁盘/服务/注入功能一律先别碰 |
| *（替代品）* **Process Explorer**（微软 Sysinternals） | 可选 | 不想用 System Informer 时的官方替代 | 双击进程 → Image 标签看 DLL |
| **x64dbg** | 第 3 课 | 免费开源调试器，看寄存器/内存/汇编，能改内存 | 反汇编、断点、单步、Dump 窗口、内存地图 |
| **Cheat Engine** | 第 6 课 | 内存扫描的"标准教学工具"，自己造轮子前先理解原理 | **只用**内存扫描 + 地址列表；不碰它的注入/脚本功能 |
| **HxD**（免费十六进制编辑器） | 可选 | 想手工翻 EXE 字节时用 | 只读打开、搜索十六进制 |

> 说明：`pe_view.py` / `scan_value.py` 只做**只读**分析，不改任何文件，也不需要管理员权限。

---

## 学习约定（你定的，我照做）

1. 不给完整修改器；不给"复制就能用"的代码。
2. 前期不碰 DLL 注入 / 代码注入 / Hook。
3. 每次只引入少量新概念，每个概念配一个能亲手做的实验。
4. 你操作 → 观察现象 → 提问 → 我再解释原理。
5. 卡住时我先告诉你"该看哪里"，而不是直接给答案。
6. 只针对**你自己拥有的单机游戏**做观察和分析；联机 / 有反作弊 / 有排行榜的游戏不在本课程范围内。
7. 你说"继续"，我才进入下一课。你贴出实验结果 / 截图 / 汇编 / 地址，我先分析你的结果再继续。

---

## 环境档案（已确认）

| 项目 | 情况 | 对课程的影响 |
|---|---|---|
| 编译器 | MSVC（Visual Studio / Build Tools） | 走 `cl.exe` + `dumpbin` 路线 |
| 系统 | Windows 10/11 x64 | — |
| 目标游戏 | Steam 版《英雄连》 | **32 位进程跑在 64 位系统上（WOW64）** |
| 可装工具 | System Informer / x64dbg / Cheat Engine 都可以 | 按阶段逐个引入 |

> ★ **重要约定**：从现在起，所有实验程序**优先编译成 32 位（x86）**。
> 用开始菜单里的 **"x86 Native Tools Command Prompt for VS"**，不是 x64 那个。
> 理由：《英雄连》是 32 位进程。位数对齐之后，地址长度、寄存器名（`eax` 而非 `rax`）、
> 调试器（`x86dbg.exe` 而非 `x64dbg.exe`）全都不会错位。
> 很多教程用 64 位讲、游戏是 32 位，新手就卡在这个缝里。

---

## 现在开始

- 第 1 课（EXE / 进程 / 变量住哪）：[`lessons/01-windows-exe.md`](lessons/01-windows-exe.md)
- **第 2 课（虚拟地址空间 / DLL / API）：[`lessons/02-process-virtual-memory.md`](lessons/02-process-virtual-memory.md)**

每做完一课，把讲义末尾【下一步】里那个清单的输出贴回来，我先分析你的结果，再写下一课。
