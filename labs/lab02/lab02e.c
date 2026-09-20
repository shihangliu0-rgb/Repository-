/*
 * lab02e.c —— 实验：自己把"一个进程的地址空间"列出来
 *             （这就是 System Informer 的 Memory 页在背后干的事）
 *
 * 目的：从"用别人的工具看"升级到"理解工具是怎么看到的"。
 *       整个程序只用一个核心 API：VirtualQueryEx。
 *       它的作用是：给我一个地址，告诉我这个地址所在的那块内存区域
 *                    从哪开始、多大、是什么类型、什么保护属性、什么状态。
 *       一段一段往后问，就能把整个地址空间走一遍。
 *
 * 用法：
 *   lab02e.exe              列出【自己】这个进程的地址空间
 *   lab02e.exe 12345        列出 PID=12345 那个进程的地址空间
 *
 * 编译：
 *   cl /Od /Zi /W3 /Fe:lab02e.exe lab02e.c
 *
 * ★ 这一课的实验 G 会让你拿它去查 lab02c.exe、notepad.exe、以及一个系统进程，
 *   然后亲眼看到"权限不够"是怎么一回事。
 */

#include <windows.h>
#include <stdio.h>
#include <stdlib.h>   /* atoi */
#include <string.h>   /* strcat, sprintf */

static const char *type_name(DWORD t)
{
    switch (t) {
        case MEM_PRIVATE: return "Private 私有";       /* malloc / VirtualAlloc / 栈 */
        case MEM_MAPPED:  return "Mapped  映射";       /* 数据文件映射、共享内存 */
        case MEM_IMAGE:   return "Image   映像";       /* EXE / DLL，被加载器映射进来的 */
        default:          return "?";
    }
}

static const char *state_name(DWORD s)
{
    switch (s) {
        case MEM_COMMIT:  return "Commit  已提交";
        case MEM_RESERVE: return "Reserve 仅预留";
        case MEM_FREE:    return "Free    空闲";
        default:          return "?";
    }
}

static void prot_name(DWORD p, char *out)
{
    char base[8];
    char extra[8];
    /* 把保护属性翻译成 RWX 三个字母，方便一眼看懂 */
    base[0] = base[1] = base[2] = '-';
    base[3] = '\0';
    switch (p & 0xFF) {
        case PAGE_READONLY:          base[0] = 'R';                            break;
        case PAGE_READWRITE:         base[0] = 'R'; base[1] = 'W';             break;
        case PAGE_WRITECOPY:         base[0] = 'R'; base[1] = 'W'; base[2]='C';break;
        case PAGE_EXECUTE:                                     base[2] = 'X';  break;
        case PAGE_EXECUTE_READ:      base[0] = 'R';            base[2] = 'X';  break;
        case PAGE_EXECUTE_READWRITE: base[0] = 'R'; base[1]='W';base[2] = 'X';  break;
        case PAGE_EXECUTE_WRITECOPY: base[0]='R'; base[1]='W'; base[2]='X';     break;
        case PAGE_NOACCESS:          /* 全 '-' */                              break;
        default:                                                               break;
    }

    /* PAGE_GUARD / PAGE_NOCACHE 是"附加标志"，可以和上面的值或在一起。
     * Guard 页是栈的边界哨兵：线程栈用超了碰到它，系统就报栈溢出。 */
    extra[0] = '\0';
    if (p & PAGE_GUARD)   strcat(extra, "+G");
    if (p & PAGE_NOCACHE) strcat(extra, "+NC");

    sprintf(out, "%s%s", base, extra);
}

int main(int argc, char **argv)
{
    DWORD target_pid;
    HANDLE hProcess;
    MEMORY_BASIC_INFORMATION mbi;
    BYTE *addr;
    BYTE *max_addr;
    int regions = 0;
    unsigned long long total_commit = 0;
    unsigned long long total_reserve = 0;
    unsigned long long total_image = 0;
    char prot[24];

    if (argc > 1) {
        target_pid = (DWORD)atoi(argv[1]);
        printf("目标 PID = %lu（别的进程）\n\n", target_pid);

        /* ★★★ 整门课最关键的一行 ★★★
         * 想读别的进程的内存，第一步永远是 OpenProcess 换句柄。
         * PROCESS_QUERY_INFORMATION  = 允许查询它的内存布局
         * PROCESS_VM_READ            = 允许读它的内存
         * 注意：这里【没有】要 PROCESS_VM_WRITE，因为这个程序只看不改。 */
        hProcess = OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ,
                               FALSE, target_pid);
        if (hProcess == NULL) {
            DWORD err = GetLastError();
            printf("!! OpenProcess 失败，错误码 %lu\n\n", err);
            if (err == 5) {
                printf("   错误码 5 = ERROR_ACCESS_DENIED 拒绝访问。\n");
                printf("   原因：目标进程的权限比你高（系统进程 / 管理员启动的进程），\n");
                printf("         或者它受 PPL（受保护进程）保护。\n");
                printf("   怎么办：用【以管理员身份运行】打开 cmd，再跑一次这个程序。\n");
                printf("   要记住的是：这个拒绝不是游戏做的，是 Windows 内核做的。\n");
            } else if (err == 87) {
                printf("   错误码 87 = ERROR_INVALID_PARAMETER，多半是这个 PID 不存在。\n");
                printf("   用 tasklist 确认一下 PID。\n");
            }
            return 1;
        }
        printf("OpenProcess 成功，拿到句柄 %p\n", (void *)hProcess);
        printf("从现在起，我就可以合法地查询/读取这个进程的内存了。\n\n");
    } else {
        target_pid = GetCurrentProcessId();
        hProcess = GetCurrentProcess();     /* 伪句柄，只对本进程有效 */
        printf("目标 PID = %lu（自己）\n\n", target_pid);
    }

#ifdef _WIN64
    max_addr = (BYTE *)0x7FFFFFFF0000ULL;
#else
    max_addr = (BYTE *)0x7FFF0000UL;        /* 32 位用户态地址空间上限（2GB） */
#endif

    printf("%-18s %-10s %-14s %-16s %s\n",
           "BaseAddress", "Size", "State", "Type", "Protect");
    printf("------------------ ---------- -------------- ---------------- -------\n");

    addr = NULL;
    while (addr < max_addr) {
        if (VirtualQueryEx(hProcess, addr, &mbi, sizeof(mbi)) == 0) {
            break;
        }

        prot_name(mbi.Protect, prot);

        /* Free 区域通常又大又多，为了看清重点，只显示 Commit 和 Reserve */
        if (mbi.State != MEM_FREE) {
            printf("0x%016llX %-10lu %-14s %-16s %s\n",
                   (unsigned long long)(size_t)mbi.BaseAddress,
                   (unsigned long)mbi.RegionSize,
                   state_name(mbi.State),
                   type_name(mbi.Type),
                   mbi.State == MEM_COMMIT ? prot : "");
            regions++;
        }

        if (mbi.State == MEM_COMMIT) {
            total_commit += mbi.RegionSize;
            if (mbi.Type == MEM_IMAGE) {
                total_image += mbi.RegionSize;
            }
        } else if (mbi.State == MEM_RESERVE) {
            total_reserve += mbi.RegionSize;
        }

        /* 走到下一个区域。注意溢出保护：地址加过头会变成 0，就会死循环 */
        {
            BYTE *next = (BYTE *)((size_t)mbi.BaseAddress + mbi.RegionSize);
            if (next <= addr) {
                break;
            }
            addr = next;
        }
    }

    printf("------------------ ---------- -------------- ---------------- -------\n");
    printf("非空闲区域共 %d 个\n", regions);
    printf("已提交 Commit  合计 %10llu KB  (其中 EXE/DLL 映像 %llu KB)\n",
           total_commit / 1024, total_image / 1024);
    printf("仅预留 Reserve 合计 %10llu KB\n", total_reserve / 1024);

    if (argc > 1) {
        CloseHandle(hProcess);      /* 用完句柄要还，这是好习惯，也是必修的规矩 */
        printf("\n已 CloseHandle。句柄一关，我就再也读不到那个进程了。\n");
    }
    return 0;
}
