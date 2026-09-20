#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scan_value.py —— 在一个"文件"里搜索一个数值（第 1 课用；第 6 课搜内存时会用到同样的思路）

用途：
    回答一个非常关键的问题：
        "money = 100 这个 100，到底存不存在于 lab01.exe 这个文件里？"

用法：
    python scan_value.py <文件> <数值> [类型]
    类型可以是: i32(默认) u32 i16 i64 f32 f64
    十六进制写法: 0x64 / 0xDEADBEEF

例子：
    python scan_value.py lab01.exe 100
    python scan_value.py lab01.exe 100 i32
    python scan_value.py RelicCOH.exe 0x1F4 f32

只用标准库，不需要安装任何东西。
"""

import struct
import sys

FORMATS = {
    "i16": ("<h", 2, "16 位有符号整数"),
    "u16": ("<H", 2, "16 位无符号整数"),
    "i32": ("<i", 4, "32 位有符号整数 (int)"),
    "u32": ("<I", 4, "32 位无符号整数 (unsigned int / DWORD)"),
    "i64": ("<q", 8, "64 位有符号整数"),
    "f32": ("<f", 4, "32 位单精度浮点 (float)"),
    "f64": ("<d", 8, "64 位双精度浮点 (double)"),
}


def parse_number(text, kind):
    text = text.strip()
    base = 16 if text.lower().startswith("0x") else 10
    value = int(text, base)
    fmt, size, desc = FORMATS[kind]
    packed = struct.pack(fmt, value)
    return value, packed, size, desc


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2

    path = sys.argv[1]
    kind = sys.argv[3] if len(sys.argv) > 3 else "i32"
    if kind not in FORMATS:
        print("未知类型 %r，可选: %s" % (kind, ", ".join(sorted(FORMATS))))
        return 2

    value, needle, size, desc = parse_number(sys.argv[2], kind)

    with open(path, "rb") as f:
        data = f.read()

    print("文件      : %s (%d 字节)" % (path, len(data)))
    print("要找的值  : %s  -> 按 %s 编码后的字节: %s" % (sys.argv[2], desc, " ".join("%02X" % b for b in needle)))
    print("-" * 60)

    hits = []
    start = 0
    while True:
        i = data.find(needle, start)
        if i < 0:
            break
        hits.append(i)
        start = i + 1  # 允许重叠，宁可多报也不漏报

    if not hits:
        print("结果      : 0 个匹配。文件里根本没有这串字节。")
        print("")
        print("这不是失败，这正是第 1 课想要你看到的现象：")
        print("  局部变量 int money = 100; 的 100 不是'存'在 EXE 里的，")
        print("  EXE 里存的是一条指令：把立即数 100 搬进某个内存位置/寄存器。")
        print("  这条指令在 x64 下长这样：  C7 45 FC 64 00 00 00   (mov dword ptr [rbp-4], 64h)")
        print("  100 (0x64) 只是这条指令里的 4 个字节，而且编译器可能换一种写法，")
        print("  比如 xor eax,eax / mov eax,64h / add ... 所以你按裸数值搜是搜不到的。")
    else:
        print("结果      : %d 个匹配（文件偏移，不是内存地址！）" % len(hits))
        for h in hits[:40]:
            print("    文件偏移 0x%08X (%10d)   前后字节: %s" % (
                h, h, " ".join("%02X" % b for b in data[max(0, h - 4):h + size + 4])))
        if len(hits) > 40:
            print("    ... 还有 %d 个，只列前 40 个" % (len(hits) - 40))
        print("")
        print("注意：这些是'文件里的偏移'。程序被加载进内存后，坐标会换成 RVA / 虚拟地址。")
        print("      文件偏移 -> 内存地址 的换算，第 2 课会用节表来做。")

    return 0


if __name__ == "__main__":
    sys.exit(main())
