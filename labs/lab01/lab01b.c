/*
 * lab01b.c  ——  第 1 课的对照组（实验 E 之后再看，先看 lab01.c）
 *
 * 同一份源码里有三种"变量住的地方"：
 *   1. 全局变量 g_money       -> 数据段（.data），编译时就分配好，值就存在 EXE 里
 *   2. main 里的局部变量 m     -> 栈（stack），main 被调用时才存在，返回就没了
 *   3. malloc 出来的 h_money   -> 堆（heap），运行时才向系统申请，free 才归还
 *
 * 编译后请做两件事：
 *   A. 运行它，看三个地址的数量级差别（栈地址通常很高，堆在中间，全局在模块基址附近）
 *   B. 用 tools/scan_value.py 在 EXE 文件里搜 100 / 200 / 300
 *      你会发现：200 和 300 能搜到，100 搜不到（或只搜到一条指令里的立即数）
 *      -> 这就是"数据在文件里" vs "数据在运行时才被造出来"的区别
 */

#include <stdio.h>
#include <stdlib.h>

int g_money = 200;          /* 全局：已初始化 -> .data 段 */
int g_zero;                 /* 全局：没初始化 -> .bss 段（文件里不占空间，只记大小） */

int main(void)
{
    volatile int m_money = 100;             /* 局部：栈 */
    int *h_money = (int *)malloc(sizeof(int));
    volatile int alive = 1;

    if (h_money == NULL) {
        printf("malloc 失败了\n");
        return 1;
    }
    *h_money = 300;                         /* 堆 */

    printf("=== lab01b：三个不同的家 ===\n");
    printf("全局 g_money : %5d   地址 %p\n", g_money, (void *)&g_money);
    printf("未初始化全局: %5d   地址 %p   (自动是 0)\n", g_zero, (void *)&g_zero);
    printf("局部 m_money : %5d   地址 %p\n", m_money, (void *)&m_money);
    printf("堆   h_money : %5d   地址 %p\n", *h_money, (void *)h_money);
    printf("代码 main    :         地址 %p\n", (void *)&main);
    fflush(stdout);

    while (alive) {
    }

    free(h_money);
    return 0;
}
