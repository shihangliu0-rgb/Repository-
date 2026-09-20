/*
 * lab02a.c —— 实验：两个进程，同一个地址，不同的内容
 *
 * 目的：亲眼验证"虚拟地址空间是每个进程私有的一份"。
 *
 * 做法：
 *   1. 程序启动后，用 VirtualAlloc 向系统申请一块内存，
 *      并且【指定】要申请在固定地址 0x12340000 上。
 *   2. 往那块地址写入一个数字。
 *   3. 死循环挂住。
 *
 * 你把它的两个实例同时跑起来，两边都会说"我在 0x12340000 写了 xxx"，
 * 地址一模一样，值不一样，而且互相看不见对方 —— 这就是虚拟内存。
 *
 * 编译（x86 Native Tools Command Prompt）：
 *   cl /Od /Zi /W3 /Fe:lab02a.exe lab02a.c
 */

#include <windows.h>
#include <stdio.h>

/* 我们"点名"要的地址。32 位进程的用户地址空间是 0x00000000 ~ 0x7FFFFFFF，
 * 0x12340000 落在中间，通常没人占用，所以系统会答应我们。 */
#define WANTED_ADDR 0x12340000

int main(void)
{
    volatile int alive = 1;
    DWORD pid = GetCurrentProcessId();

    /* VirtualAlloc：直接向系统要地址空间。
     * 参数依次是：想要的地址、大小、分配方式、页保护属性。
     * MEM_RESERVE|MEM_COMMIT = 既占住这段地址范围，又真的给它配上物理存储。
     * PAGE_READWRITE         = 这段内存可读可写、不可执行。 */
    int *p = (int *)VirtualAlloc((LPVOID)WANTED_ADDR,
                                 4096,
                                 MEM_RESERVE | MEM_COMMIT,
                                 PAGE_READWRITE);

    if (p == NULL) {
        printf("VirtualAlloc 失败了，错误码 %lu\n", GetLastError());
        printf("（可能是这个地址已经被别的模块占了，改一个再试，比如 0x12350000）\n");
        return 1;
    }

    /* 写入一个和 PID 有关的值，这样两个实例的值一定不同 */
    *p = 1000 + (int)(pid % 900);

    printf("=== lab02a ===\n");
    printf("我的 PID              = %lu\n", pid);
    printf("我要求的地址          = 0x%08X\n", WANTED_ADDR);
    printf("系统实际给我的地址    = %p\n", (void *)p);
    printf("我在这个地址写入的值  = %d\n", *p);
    printf("\n");
    printf("★ 现在请再双击一次这个 EXE，开第二个实例。\n");
    printf("  你会发现第二个实例也拿到了 0x%08X，但写进去的值不一样。\n", WANTED_ADDR);
    printf("  去 System Informer 里看这两个进程，它们各自都有一段 0x12340000 的 Private 内存。\n");
    printf("\n本进程挂住不退，按 Ctrl+C 结束。\n");
    fflush(stdout);

    while (alive) {
        Sleep(200);
    }

    VirtualFree(p, 0, MEM_RELEASE);
    return 0;
}
