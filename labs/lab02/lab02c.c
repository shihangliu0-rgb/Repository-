/*
 * lab02c.c —— 实验：亲眼看堆长大，以及"预留(Reserved)"和"提交(Commit)"的区别
 *
 * 目的：理解任务管理器 / System Informer 里那几个内存数字到底在说什么。
 *
 * 三个关键概念：
 *   Reserved（预留）  = 这段地址范围被占住了，别人不能用，但还没有配上物理存储，
 *                       不能读也不能写。它只消耗"地址空间"，不消耗内存。
 *   Committed（提交） = 系统承诺：你要写的话，我一定拿得出物理页/页面文件给你。
 *                       这才是"占内存"。
 *   Working Set       = 此刻真的驻留在物理内存(RAM)里的那部分。
 *                       被换出去的页不算，但仍然是 Committed。
 *
 * 程序行为：每 3 秒 malloc 一块 10MB 并真的写满，一共 10 块，
 *           每次都把当前的 Commit / WorkingSet 数字打印出来。
 *           你同时在 System Informer 里看着它的 Memory 页，会看到新区域一块块冒出来。
 *
 * 编译：
 *   cl /Od /Zi /W3 /Fe:lab02c.exe lab02c.c psapi.lib
 *   （如果链接报错找不到 GetProcessMemoryInfo，就把 psapi.lib 加上；
 *     新版 SDK 里它已经在 kernel32 里了，不加也能过）
 */

#include <windows.h>
#include <stdio.h>
#include <stdlib.h>   /* malloc, free */
#include <string.h>   /* memset */
#include <psapi.h>

#define CHUNK (10 * 1024 * 1024)   /* 每次 10 MB */
#define ROUNDS 10

static void report(int round, void *newest, size_t total)
{
    PROCESS_MEMORY_COUNTERS pmc;
    MEMORY_BASIC_INFORMATION mbi;

    ZeroMemory(&pmc, sizeof(pmc));
    pmc.cb = sizeof(pmc);

    if (!GetProcessMemoryInfo(GetCurrentProcess(), &pmc, sizeof(pmc))) {
        printf("GetProcessMemoryInfo 失败，错误码 %lu\n", GetLastError());
        return;
    }

    printf("第 %2d 轮  已申请 %4.0f MB | CommitCharge %6.0f KB | WorkingSet %6.0f KB | Peak WS %6.0f KB\n",
           round,
           (double)total / (1024.0 * 1024.0),
           pmc.PrivateUsage / 1024.0,
           pmc.WorkingSetSize / 1024.0,
           pmc.PeakWorkingSetSize / 1024.0);

    /* 顺便看看这块新内存的区域属性 —— 这就是 System Informer 的 Memory 页显示的东西 */
    if (newest != NULL && VirtualQuery(newest, &mbi, sizeof(mbi)) != 0) {
        printf("         新区块 %p : 区域大小 %8lu KB, 类型 0x%lX, 保护 0x%lX, 状态 0x%lX\n",
               newest,
               (unsigned long)(mbi.RegionSize / 1024),
               mbi.Type, mbi.Protect, mbi.State);
        printf("         (类型 0x20000=MEM_PRIVATE 私有, 0x40000=MEM_MAPPED, 0x1000000=MEM_IMAGE)\n");
        printf("         (状态 0x1000=MEM_COMMIT 已提交, 0x2000=MEM_RESERVE 仅预留, 0x10000=MEM_FREE 空闲)\n");
    }
    fflush(stdout);
}

int main(void)
{
    void *blocks[ROUNDS];
    size_t total = 0;
    int i;
    volatile int alive = 1;

    printf("=== lab02c：堆会长大 ===\n");
    printf("PID = %lu\n\n", GetCurrentProcessId());
    printf("★ 现在就把 System Informer 打开，双击本进程，切到 Memory 页，然后回来看这里。\n\n");

    report(0, NULL, 0);
    printf("\n");

    for (i = 0; i < ROUNDS; i++) {
        unsigned char *p = (unsigned char *)malloc(CHUNK);
        if (p == NULL) {
            printf("malloc 失败（内存不够了），停在第 %d 轮\n", i);
            break;
        }
        /* 必须真的写一遍！只 malloc 不写的话，很多页还停留在"提交了但没碰过"的状态，
         * WorkingSet 不会涨，你就看不到物理内存被真正占用。 */
        memset(p, 0xAB, CHUNK);

        blocks[i] = p;
        total += CHUNK;
        report(i + 1, p, total);
        Sleep(3000);
    }

    printf("\n=== 分配结束，总共 %4.0f MB ===\n", (double)total / (1024.0 * 1024.0));
    printf("★ 现在去 System Informer 的 Memory 页，按 Size 排序，\n");
    printf("  你应该能看到若干块巨大的 Private / Commit / RW 区域，那就是刚才 malloc 出来的堆。\n");
    printf("  数一数有几块、每块多大，和上面打印的 10 轮对得上吗？（不一定正好 10 块，想想为什么）\n\n");
    printf("挂住不退，你可以慢慢看。按 Ctrl+C 结束。\n");
    fflush(stdout);

    while (alive) {
        Sleep(500);
    }

    for (i = 0; i < ROUNDS; i++) {
        free(blocks[i]);
    }
    return 0;
}
