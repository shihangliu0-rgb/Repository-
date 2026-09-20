/*
 * lab01.c  ——  第 1 课的"小白鼠"
 *
 * 编译方式见 lessons/01-windows-exe.md
 *
 * 这个程序刻意做得很笨：
 *   - 声明一个 int money = 100;
 *   - 把它的地址和值打印出来
 *   - 然后死循环不退出
 * 目的不是写出好程序，而是给操作系统/调试器一个"活的、不动的"观察对象。
 */

#include <stdio.h>

int main(void)
{
    int money = 100;

    /* volatile: 告诉编译器"这个变量随时可能被别人改，别自作聪明地优化掉它"。
     * 没有它的话，Release 编译时编译器会发现 money 永远等于 100，
     * 直接把整个循环删掉 —— 那我们就没东西可观察了。 */
    volatile int alive = 1;

    printf("=== lab01 ===\n");
    printf("money      = %d\n", money);
    printf("&money     = %p        <- money 这个变量的地址\n", (void *)&money);
    printf("sizeof(int)= %d 字节\n", (int)sizeof(int));
    printf("main       = %p        <- 代码也是一种'有地址的东西'\n", (void *)&main);
    printf("我现在不退出，你可以去任务管理器 / 调试器里找我。\n");
    printf("按 Ctrl+C 结束。\n");
    fflush(stdout);

    while (alive) {
        /* 空转。这里故意什么都不做，
         * 因为"什么都不做"的进程最容易观察：它的内存不会自己变化。 */
    }

    return 0; /* 永远走不到这里，但写上让编译器闭嘴 */
}
