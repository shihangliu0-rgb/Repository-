@echo off
REM =====================================================================
REM  build_lab02.bat —— 一键编译第 2 课的全部实验程序
REM
REM  ★ 请在 "x86 Native Tools Command Prompt for VS 2022" 里运行本脚本，
REM    因为最终目标《英雄连》是 32 位进程。
REM    想看 64 位的对比，就再在 x64 提示符里跑一遍，输出文件名自己改。
REM
REM  产物：
REM    lab02a.exe  两个进程抢同一个地址（虚拟地址空间隔离）
REM    lab02b.exe  一个进程四个线程（各自的栈）
REM    lab02c.exe  堆会长大（Commit / WorkingSet 的区别）
REM    lab02d.exe  模块基址 / ASLR / 基址+RVA=地址
REM    lab02e.exe  自己走一遍地址空间（VirtualQueryEx），可查别的 PID
REM =====================================================================
setlocal
chcp 65001 >nul
cd /d "%~dp0"

where cl.exe >nul 2>nul
if not %errorlevel%==0 (
    echo !! 找不到 cl.exe
    echo !! 请从开始菜单打开 "x86 Native Tools Command Prompt for VS 2022"，
    echo !! 然后 cd 到本目录再运行 build_lab02.bat
    exit /b 1
)

echo.
echo [1/3] 编译 Debug 版（/Od 不优化，变量才会老老实实待在内存里）...
for %%f in (lab02a lab02b lab02c lab02d lab02e) do (
    echo     cl %%f.c
    cl /nologo /Od /Zi /W3 /Fe:%%f.exe %%f.c psapi.lib > nul
    if errorlevel 1 (
        echo     !! %%f.c 编译失败，重新显示错误：
        cl /nologo /Od /Zi /W3 /Fe:%%f.exe %%f.c psapi.lib
    )
)

echo.
echo [2/3] 编译一个 Release 版做对照（只看 lab02c，用来体会优化带来的差别）...
cl /nologo /O2 /W3 /Fe:lab02c_release.exe lab02c.c psapi.lib > nul

echo.
echo [3/3] 结果：
dir /b *.exe

echo.
echo =====================================================================
echo  下一步：打开 lessons\02-process-virtual-memory.md，从实验 A 开始。
echo  别忘了先装 System Informer（讲义里写了下载地址和只用哪些功能）。
echo =====================================================================
endlocal
