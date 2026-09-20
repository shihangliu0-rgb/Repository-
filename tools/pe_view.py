#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pe_view.py —— 一个"够用就好"的 PE 文件观察器（只读，不修改任何文件）

用途：
    把一个 .exe / .dll 当成"数据"打开，看看 Windows 加载器需要知道的信息都写在哪里。
    第 1 课用它看自己编译出来的 lab01.exe，第 7 课用它看游戏的 EXE / DLL。

用法：
    python pe_view.py <文件路径>
    python pe_view.py C:\\lab\\lab01.exe

只用 Python 标准库（struct），不需要安装任何东西。
"""

import struct
import sys

IMAGE_FILE_MACHINE = {
    0x014C: "i386 (32 位 / x86)",
    0x8664: "AMD64 (64 位 / x64)",
    0x01C0: "ARM",
    0xAA64: "ARM64",
}

IMAGE_FILE_CHARACTERISTICS = [
    (0x0002, "EXECUTABLE_IMAGE 可执行"),
    (0x0020, "LARGE_ADDRESS_AWARE 能感知 >2GB 地址"),
    (0x0100, "32BIT_MACHINE 32 位机器"),
    (0x2000, "DLL 这是一个 DLL，不是 EXE"),
]

DLL_CHARACTERISTICS = [
    (0x0040, "DYNAMIC_BASE  -> ASLR：每次启动基址可以不同"),
    (0x0100, "NX_COMPAT     -> DEP：数据页默认不可执行"),
    (0x0400, "NO_SEH        -> 不使用 SEH"),
    (0x8160, "HIGH_ENTROPY_VA / TERMINAL_SERVER_AWARE 等"),
]


def flags(value, table):
    """把一个整数标志位翻译成人类能读的文字列表。"""
    out = []
    for bit, text in table:
        if value & bit:
            out.append("    [x] 0x%04X  %s" % (bit, text))
    return "\n".join(out) if out else "    (无)"


def main(path):
    with open(path, "rb") as f:
        data = f.read()

    print("=" * 68)
    print("文件: %s" % path)
    print("大小: %d 字节 (%.1f KB)" % (len(data), len(data) / 1024.0))
    print("=" * 68)

    # ---------- 1) DOS 头：文件最开头的 64 字节 ----------
    if len(data) < 0x40 or data[0:2] != b"MZ":
        print("!! 开头不是 'MZ'，这不是一个 PE 文件（EXE/DLL）。")
        print("   提示：ELF(Linux) / Mach-O(macOS) / 纯文本 都会在这里被拒绝。")
        return 1

    e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
    print("\n[1] DOS 头 (偏移 0x00)")
    print("    魔数            : %r   <- 所有 EXE 的头两个字节永远是 'MZ'" % data[0:2])
    print("    e_lfanew        : 0x%X  <- 真正的 PE 头在这个偏移处" % e_lfanew)

    # ---------- 2) PE 签名 ----------
    if data[e_lfanew:e_lfanew + 4] != b"PE\x00\x00":
        print("!! 在 e_lfanew 处没找到 'PE\\0\\0' 签名，文件可能损坏。")
        return 1
    print("\n[2] PE 签名 (偏移 0x%X)" % e_lfanew)
    print("    Signature       : %r  <- 'PE' + 两个 0" % data[e_lfanew:e_lfanew + 4])

    coff = e_lfanew + 4
    machine, nsec, tstamp, _, _, optsize, chars = struct.unpack_from("<HHIIIHH", data, coff)

    # ---------- 3) COFF 文件头 ----------
    print("\n[3] COFF 文件头 (偏移 0x%X)" % coff)
    print("    Machine         : 0x%04X  %s" % (machine, IMAGE_FILE_MACHINE.get(machine, "未知")))
    print("    NumberOfSections: %d" % nsec)
    print("    TimeDateStamp   : 0x%08X (链接时间戳)" % tstamp)
    print("    SizeOfOptionalHdr: %d 字节" % optsize)
    print("    Characteristics :\n%s" % flags(chars, IMAGE_FILE_CHARACTERISTICS))

    # ---------- 4) 可选头（其实一点都不"可选"） ----------
    opt = coff + 20
    magic = struct.unpack_from("<H", data, opt)[0]
    pe32plus = (magic == 0x20B)
    print("\n[4] Optional Header (偏移 0x%X)" % opt)
    print("    Magic           : 0x%X  -> %s" % (magic, "PE32+ (64 位)" if pe32plus else "PE32 (32 位)"))

    if pe32plus:
        entry, base = struct.unpack_from("<IQ", data, opt + 16)
        sub_off, dllchar_off = opt + 68, opt + 70
        size_of_image = struct.unpack_from("<I", data, opt + 56)[0]
    else:
        entry, base = struct.unpack_from("<II", data, opt + 16)
        sub_off, dllchar_off = opt + 68, opt + 70
        size_of_image = struct.unpack_from("<I", data, opt + 56)[0]

    subsystem, dllchar = struct.unpack_from("<HH", data, sub_off)
    align_fa, align_sec = struct.unpack_from("<II", data, opt + 32)

    sub_name = {1: "NATIVE 驱动", 2: "WINDOWS_GUI 图形界面", 3: "WINDOWS_CUI 控制台"}.get(subsystem, str(subsystem))

    print("    AddressOfEntryPoint: 0x%X   <- 进程启动后 CPU 从这里开始跑（不是 main！）" % entry)
    print("    ImageBase          : 0x%X   <- 文件希望被加载到这个基址" % base)
    print("    SizeOfImage        : 0x%X (%d KB) <- 加载后在内存里占的虚拟地址范围" % (size_of_image, size_of_image // 1024))
    print("    SectionAlignment   : 0x%X  (内存里按这个对齐)" % align_sec)
    print("    FileAlignment      : 0x%X  (文件里按这个对齐)" % align_fa)
    print("    Subsystem          : %d -> %s" % (subsystem, sub_name))
    print("    DllCharacteristics :\n%s" % flags(dllchar, DLL_CHARACTERISTICS))

    # ---------- 5) 节表 ----------
    sect = opt + optsize
    print("\n[5] 节表 Section Table (偏移 0x%X)" % sect)
    print("    %-9s %-12s %-12s %-12s %-12s %s" % ("Name", "VirtSize", "VirtAddr(RVA)", "RawSize", "RawOffset", "Characteristics"))
    print("    " + "-" * 92)
    for i in range(nsec):
        o = sect + i * 40
        name = data[o:o + 8].rstrip(b"\x00").decode("latin1")
        vsize, vaddr, rsize, roff = struct.unpack_from("<IIII", data, o + 8)
        schar = struct.unpack_from("<I", data, o + 36)[0]
        marks = []
        if schar & 0x20000000:
            marks.append("CODE 代码")
        if schar & 0x40000000:
            marks.append("IDATA 已初始化数据")
        if schar & 0x80000000:
            marks.append("UDATA 未初始化数据")
        if schar & 0x20000000 and schar & 0x8:
            marks.append("可执行")
        if schar & 0x80000000 and not (schar & 0x40000000):
            marks.append("可读写")
        print("    %-9s 0x%010X 0x%010X 0x%010X 0x%010X %s" % (name, vsize, vaddr, rsize, roff, ",".join(marks)))

    # ---------- 6) 导入表：这个 EXE 依赖哪些 DLL ----------
    print("\n[6] 导入的 DLL（这个程序要用别人的代码）")
    try:
        if pe32plus:
            import_rva, import_size = struct.unpack_from("<QQ", data, opt + 112)
        else:
            import_rva, import_size = struct.unpack_from("<II", data, opt + 96)
    except struct.error:
        import_rva, import_size = 0, 0

    def rva_to_off(rva):
        for i in range(nsec):
            o = sect + i * 40
            vsize, vaddr, rsize, roff = struct.unpack_from("<IIII", data, o + 8)
            if vaddr <= rva < vaddr + max(vsize, rsize):
                return roff + (rva - vaddr)
        return None

    if import_rva == 0:
        print("    (没有导入表)")
    else:
        off = rva_to_off(import_rva)
        if off is None:
            print("    (导入表 RVA 0x%X 不在任何节里)" % import_rva)
        else:
            count = 0
            while True:
                ent = data[off + count * 20: off + count * 20 + 20]
                if len(ent) < 20:
                    break
                name_rva = struct.unpack_from("<I", ent, 12)[0]
                if name_rva == 0:
                    break
                no = rva_to_off(name_rva)
                if no is None:
                    break
                end = data.index(b"\x00", no)
                print("    - %s" % data[no:end].decode("latin1"))
                count += 1
                if count > 64:
                    break

    print("\n" + "=" * 68)
    print("看这份输出时，请重点记住三件事：")
    print("  A. ImageBase  +  EntryPoint  = 加载器需要把文件搬到哪、CPU 从哪开始")
    print("  B. 节表里的 RVA / RawOffset  = 同一份数据'在文件里'和'在内存里'的两个坐标")
    print("  C. DllCharacteristics 里的 DYNAMIC_BASE = 这个 EXE 支不支持 ASLR")
    print("=" * 68)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
