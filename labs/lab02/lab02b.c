/*
 * lab02b.c —— 实验：一个进程里的多个线程，各有各的栈
 *
 * 目的：看清楚"进程 = 资源容器，线程 = 执行单位"这句话在内存里长什么样。
 *
 * 现象：
 *   主线程 + 3 个新线程 = 4 个线程。
 *   它们共享同一份地址空间（都能看到同一个全局变量），
 *   但每个线程都有【自己独立的一块栈内存】。
 *   程序会把 4 个栈上局部变量的地址都打印出来 —— 你会发现它们分散在 4 个不同的区域。
 *
 * 编译：
 *   cl /Od /Zi /W3 /Fe:lab02b.exe lab02b.c
 */

#include <windows.h>
#include <stdio.h>

/* 全局变量：所有线程共享同一份 */
volatile long g_shared_counter = 0;

struct ThreadArg {
    int id;
};

static DWORD WINAPI worker(LPVOID param)
{
    struct ThreadArg *arg = (struct ThreadArg *)param;
    int local_on_stack = arg->id * 111;      /* 这个变量住在本线程自己的栈上 */
    volatile int alive = 1;

    printf("[线程 %d] TID=%5lu  局部变量 local_on_stack 的地址 = %p  值 = %d\n",
           arg->id,
           GetCurrentThreadId(),
           (void *)&local_on_stack,
           local_on_stack);
    fflush(stdout);

    /* 每个线程都去改同一个全局变量。
     * InterlockedIncrement 是"原子加一"，保证 4 个线程一起加不会互相踩掉。
     * （这里用它是为了让计数准确，不是为了讲多线程同步 —— 那是另一门课。） */
    while (alive) {
        InterlockedIncrement(&g_shared_counter);
        Sleep(500);
        /* 跑 20 次就停，免得计数器涨太快看不清 */
        if (g_shared_counter > 80) {
            break;
        }
    }
    return 0;
}

int main(void)
{
    HANDLE threads[3];
    struct ThreadArg args[3];
    int i;
    int main_local = 999;                    /* 主线程的栈上变量 */
    volatile int alive = 1;

    printf("=== lab02b：一个进程，四个线程 ===\n");
    printf("进程 PID                  = %lu\n", GetCurrentProcessId());
    printf("[主线程 ] TID=%5lu  局部变量 main_local      的地址 = %p  值 = %d\n",
           GetCurrentThreadId(), (void *)&main_local, main_local);
    printf("[全局   ] g_shared_counter 的地址 = %p  （4 个线程共享这一个）\n",
           (void *)&g_shared_counter);
    printf("\n");

    for (i = 0; i < 3; i++) {
        args[i].id = i + 1;
        threads[i] = CreateThread(NULL,          /* 默认安全属性 */
                                  0,             /* 默认栈大小 = 1MB（预留） */
                                  worker,
                                  &args[i],
                                  0,             /* 立即开始运行 */
                                  NULL);
        if (threads[i] == NULL) {
            printf("CreateThread 失败，错误码 %lu\n", GetLastError());
            return 1;
        }
    }

    printf("\n★ 现在去 System Informer：\n");
    printf("  1) 双击本进程 -> Threads 页：应该看到 4 个线程（含主线程）\n");
    printf("  2) 双击本进程 -> Memory 页：找出 4 块彼此分开的 Private / RW 内存，\n");
    printf("     它们的地址范围应该分别覆盖上面打印的 4 个局部变量地址 —— 那就是 4 个栈\n");
    printf("  3) 观察下面这行计数器：4 个线程在同时改同一个全局变量\n\n");

    while (alive) {
        printf("g_shared_counter = %ld   （地址始终是 %p，不变）\r",
               g_shared_counter, (void *)&g_shared_counter);
        fflush(stdout);
        Sleep(300);
    }

    return 0;
}
