@echo off
REM =====================================================================
REM  build_lab01.bat —— 一键编译第 1 课的实验程序（Windows 上双击运行）
REM
REM  它做的事：
REM    1. 找到 MSVC 编译器 (cl.exe)，找不到就退回 g++
REM    2. 编译出 lab01_debug.exe  (不优化，方便观察)
REM    3. 编译出 lab01_release.exe(/O2 优化，用来"看编译器把循环删掉")
REM    4. 用 dumpbin 反汇编 main，把 100 (0x64) 那条指令找出来
REM
REM  注意：这是学习脚本，故意写得直白，没有任何工程包装。
REM =====================================================================
setlocal
cd /d "%~dp0"

echo.
echo [1/4] 寻找编译器...
where cl.exe >nul 2>nul
if %errorlevel%==0 (
    set CC=cl
    echo     找到 MSVC cl.exe
    goto :have_cl
)

REM 没在 PATH 里找到 cl，试着用 vswhere 定位 Visual Studio
set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if exist "%VSWHERE%" (
    for /f "usebackq tokens=*" %%i in (`"%VSWHERE%" -latest -property installationPath`) do set "VSPATH=%%i"
    if defined VSPATH (
        echo     找到 Visual Studio: %VSPATH%
        call "%VSPATH%\VC\Auxiliary\Build\vcvars64.bat" >nul
        where cl.exe >nul 2>nul && set CC=cl && goto :have_cl
    )
)

where g++.exe >nul 2>nul
if %errorlevel%==0 (
    set CC=g++
    echo     没找到 cl.exe，改用 MinGW g++
    goto :have_gcc
)

echo     !! cl.exe 和 g++.exe 都没找到。
echo     !! 请先安装其一：
echo     !!   A) Visual Studio Build Tools ^(勾选 "使用 C++ 的桌面开发"^)
echo     !!   B) MSYS2:  pacman -S mingw-w64-x86_64-gcc
exit /b 1

:have_cl
echo.
echo [2/4] 编译 Debug 版（/Od 不优化 /Zi 带调试信息）...
cl /nologo /Od /Zi /W3 /Fe:lab01_debug.exe   lab01.c
cl /nologo /Od /Zi /W3 /Fe:lab01b_debug.exe  lab01b.c
echo [3/4] 编译 Release 版（/O2 优化）...
cl /nologo /O2 /W3 /Fe:lab01_release.exe  lab01.c
cl /nologo /O2 /W3 /Fe:lab01b_release.exe lab01b.c
goto :dump

:have_gcc
echo.
echo [2/4] 编译 Debug 版（-O0 不优化 -g 带调试信息）...
g++ -O0 -g -Wall -o lab01_debug.exe   lab01.c
g++ -O0 -g -Wall -o lab01b_debug.exe  lab01b.c
echo [3/4] 编译 Release 版（-O2 优化）...
g++ -O2 -Wall -o lab01_release.exe  lab01.c
g++ -O2 -Wall -o lab01b_release.exe lab01b.c
goto :dump

:dump
echo.
echo [4/4] 反汇编 main，找找 100 (十六进制 0x64) 藏在哪...
where dumpbin.exe >nul 2>nul
if %errorlevel%==0 (
    dumpbin /disasm /symbols lab01_debug.exe > lab01_debug.disasm.txt
    echo     已写入 lab01_debug.disasm.txt
    findstr /i /c:"00000064" /c:",64h" lab01_debug.disasm.txt
) else (
    where objdump.exe >nul 2>nul
    if %errorlevel%==0 (
        objdump -d -M intel lab01_debug.exe > lab01_debug.disasm.txt
        echo     已写入 lab01_debug.disasm.txt
        findstr /i /c:"0x64" lab01_debug.disasm.txt
    ) else (
        echo     没找到 dumpbin / objdump，跳过反汇编（不影响后面的实验）
    )
)

echo.
echo =====================================================================
echo  完成。现在你应该有这些文件：
echo    lab01_debug.exe    lab01_release.exe
echo    lab01b_debug.exe   lab01b_release.exe
echo  下一步：按 lessons\01-windows-exe.md 里的实验 B 开始动手。
echo =====================================================================
endlocal
