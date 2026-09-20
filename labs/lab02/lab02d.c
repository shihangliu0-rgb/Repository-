/*
 * lab02d.c —— 实验：模块基址、ASLR、以及"基址 + 偏移 = 地址"
 *
 * 目的：这一课最重要的一个实验。第 7 课的"模块基址 -> 偏移 -> 指针 -> 数据"
 *       整条链，起点就是这里打印出来的 Base 那一列。
 *
 * 程序行为：
 *   1. 打印自己的 EXE 实际被加载到的基址，和 PE 文件里写的 ImageBase 对比
 *      -> 如果两者不同，说明 ASLR 生效了，系统给它换了个位置
 *   2. 列出本进程加载的所有模块（EXE + 每个 DLL），以及各自的基址和大小
 *      -> 数一数：你的 20 行源码，实际拖进来多少个 DLL？
 *   3. 演示一次"基址 + 偏移 = 虚拟地址"的计算，并用 ReadProcessMemory 验证它
 *
 * 编译（需要额外链接 psapi）：
 *   cl /Od /Zi /W3 /Fe:lab02d.exe lab02d.c psapi.lib
 *
 * ★ 多做一次：编译两遍，一遍用 x86 提示符、一遍用 x64 提示符，
 *   对比两者的 ImageBase 和实际基址，你会看到 32 位和 64 位的地址空间完全不是一回事。
 */

#include <windows.h>
#include <stdio.h>
#include <psapi.h>

static const char *prot_name(DWORD p)
{
    switch (p & 0xFF) {
        case PAGE_NOACCESS:          return "PAGE_NOACCESS      ---    不可访问";
        case PAGE_READONLY:          return "PAGE_READONLY      R--    只读（常量、字符串）";
        case PAGE_READWRITE:         return "PAGE_READWRITE     RW-    可读写（全局变量、堆、栈）";
        case PAGE_WRITECOPY:         return "PAGE_WRITECOPY     RW-C   写时复制";
        case PAGE_EXECUTE:           return "PAGE_EXECUTE       --X    只执行";
        case PAGE_EXECUTE_READ:      return "PAGE_EXECUTE_READ  R-X    可读可执行（代码段）";
        case PAGE_EXECUTE_READWRITE: return "PAGE_EXECUTE_READWRITE RWX 可读写可执行（自修改代码/JIT）";
        case PAGE_EXECUTE_WRITECOPY: return "PAGE_EXECUTE_WRITECOPY  RWXC";
        default:                     return "(未知)";
    }
}

int main(void)
{
    HMODULE mods[1024];
    HMODULE hSelf;
    DWORD needed = 0;
    unsigned int i;
    unsigned int count = 0;
    char path[MAX_PATH];
    volatile int alive = 1;

    /* 拿到 EXE 自己的句柄。参数传 NULL 就是"主模块"，也就是你的 EXE。
     * （所有变量声明都放在函数开头，是为了让 MSVC 的默认 C 模式也能编译过。） */
    hSelf = GetModuleHandleA(NULL);

    printf("=== lab02d：模块基址 ===\n");
    printf("PID                       = %lu\n", GetCurrentProcessId());
    printf("EXE 实际加载基址 (hSelf)  = %p\n", (void *)hSelf);

    /* ---- 1. 读 PE 头，看文件里"希望"的基址是多少 ---- */
    {
        BYTE *base = (BYTE *)hSelf;
        IMAGE_DOS_HEADER *dos = (IMAGE_DOS_HEADER *)base;
        IMAGE_NT_HEADERS *nt;

        if (dos->e_magic != IMAGE_DOS_SIGNATURE) {   /* 'MZ' */
            printf("!! 基址处不是 MZ，出错了\n");
            return 1;
        }
        nt = (IMAGE_NT_HEADERS *)(base + dos->e_lfanew);
        if (nt->Signature != IMAGE_NT_SIGNATURE) {   /* 'PE\0\0' */
            printf("!! 没找到 PE 签名\n");
            return 1;
        }

        printf("PE 文件里写的 ImageBase   = 0x%llX\n",
               (unsigned long long)nt->OptionalHeader.ImageBase);
        printf("AddressOfEntryPoint(RVA)  = 0x%08lX\n",
               nt->OptionalHeader.AddressOfEntryPoint);
        printf("入口点的真实虚拟地址      = %p   (= 基址 + RVA)\n",
               (void *)(base + nt->OptionalHeader.AddressOfEntryPoint));
        printf("DllCharacteristics        = 0x%04X  %s\n",
               nt->OptionalHeader.DllCharacteristics,
               (nt->OptionalHeader.DllCharacteristics & 0x0040)
                   ? "-> 有 IMAGE_DLLCHARACTERISTICS_DYNAMIC_BASE，支持 ASLR"
                   : "-> 没有 DYNAMIC_BASE，不支持 ASLR（基址永远固定）");

        if ((size_t)hSelf == (size_t)nt->OptionalHeader.ImageBase) {
            printf("\n★ 实际基址 == ImageBase：这次没被随机化（或者本来就不支持 ASLR）。\n");
        } else {
            printf("\n★ 实际基址 != ImageBase：ASLR 生效了！系统把它挪了 0x%X 字节。\n",
                   (unsigned int)((size_t)hSelf - (size_t)nt->OptionalHeader.ImageBase));
            printf("  这就是为什么你在 PE 文件里算出来的地址，不能直接拿去用在运行中的进程上。\n");
            printf("  多运行几次这个程序，看看基址会不会变。\n");
        }
    }

    /* ---- 2. 列出所有模块 ---- */
    printf("\n=== 本进程加载的模块（EXE + DLL） ===\n");
    if (!EnumProcessModules(GetCurrentProcess(), mods, sizeof(mods), &needed)) {
        printf("EnumProcessModules 失败，错误码 %lu\n", GetLastError());
    } else {
        count = (unsigned int)(needed / sizeof(HMODULE));
        printf("共 %u 个模块\n\n", count);
        printf("%-4s %-18s %-10s %s\n", "#", "Base 基址", "Size", "Path");
        printf("---- ------------------ ---------- --------------------------------\n");
        for (i = 0; i < count && i < 1024; i++) {
            MODULEINFO mi;
            ZeroMemory(&mi, sizeof(mi));
            GetModuleInformation(GetCurrentProcess(), mods[i], &mi, sizeof(mi));
            path[0] = '\0';
            GetModuleFileNameExA(GetCurrentProcess(), mods[i], path, MAX_PATH);
            printf("%-4u 0x%016llX 0x%08lX %s%s\n",
                   i,
                   (unsigned long long)(size_t)mi.lpBaseOfDll,
                   mi.SizeOfImage,
                   path,
                   (mi.lpBaseOfDll == (LPVOID)hSelf) ? "   <== 这就是你的 EXE" : "");
        }
    }

    /* ---- 3. 验证"基址 + 偏移 = 虚拟地址" ---- */
    printf("\n=== 验证：基址 + RVA = 真实地址 ===\n");
    {
        /* main 函数的地址减去模块基址，就是 main 的 RVA */
        BYTE *pmain = (BYTE *)(size_t)&main;
        size_t rva = (size_t)pmain - (size_t)hSelf;
        BYTE *computed = (BYTE *)hSelf + rva;

        printf("main 的真实地址           = %p\n", (void *)pmain);
        printf("模块基址                  = %p\n", (void *)hSelf);
        printf("main 的 RVA (偏移)        = 0x%X\n", (unsigned int)rva);
        printf("基址 + RVA 算回来         = %p   %s\n",
               (void *)computed,
               (computed == pmain) ? "-> 一致 ✔" : "-> 不一致 ✘");

        /* 用 ReadProcessMemory 读自己进程里 main 的前 16 个字节。
         * 读到的就是机器指令本身 —— 代码确实就躺在这个地址上。 */
        {
            unsigned char buf[16];
            SIZE_T rd = 0;
            printf("\nmain 开头的 16 个字节（机器指令）：\n");
            if (ReadProcessMemory(GetCurrentProcess(), computed, buf, sizeof(buf), &rd)) {
                unsigned int k;
                printf("  ");
                for (k = 0; k < rd; k++) {
                    printf("%02X ", buf[k]);
                }
                printf("\n");
                printf("  对照 dumpbin /disasm 的输出，头几个字节应该完全一样。\n");
            } else {
                printf("  ReadProcessMemory 失败，错误码 %lu\n", GetLastError());
            }
        }

        /* ★ 关键的对比实验：把 PID 当成 HANDLE 用，看看会发生什么 */
        printf("\n=== 陷阱演示：PID 不是 HANDLE ===\n");
        {
            unsigned char buf[4];
            SIZE_T rd = 0;
            DWORD mypid = GetCurrentProcessId();
            BOOL ok = ReadProcessMemory((HANDLE)(size_t)mypid, computed, buf, sizeof(buf), &rd);
            printf("ReadProcessMemory((HANDLE)%lu, ...) 返回 %s，错误码 %lu\n",
                   mypid, ok ? "成功" : "失败", GetLastError());
            printf("-> 失败是正常的！PID 只是一个编号，HANDLE 是句柄表里的一个引用。\n");
            printf("   想读别的进程，必须先 OpenProcess 换来一个 HANDLE。这是第 10 课的内容。\n");
            printf("   （读自己进程时可以用 GetCurrentProcess() 这个'伪句柄'，它永远是 (HANDLE)-1）\n");
        }
    }

    printf("\n挂住不退，你可以去 System Informer 的 Modules 页对照。按 Ctrl+C 结束。\n");
    fflush(stdout);
    while (alive) {
        Sleep(500);
    }
    return 0;
}
