#!/usr/bin/env python3
"""仓库自检脚本：在没有 ROS 的机器上也能快速发现低级错误。

用法:
    python3 scripts/check_repo.py

检查内容:
    1. 所有 .py 文件语法（含 launch 文件）
    2. 所有 package.xml / *.xacro / *.sdf 的 XML 合法性
    3. 所有 *.yaml / *.rviz 的 YAML 合法性（需要 pyyaml，缺失则跳过）
    4. ament_python 包结构完整性（resource 标记、setup.cfg、入口模块存在）
"""

import glob
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

failures = []


def check(cond, msg):
    if not cond:
        failures.append(msg)
        print(f'  ✘ {msg}')
    return cond


def python_syntax():
    files = sorted(glob.glob('**/*.py', recursive=True))
    files = [f for f in files if not f.startswith(('build/', 'install/', 'log/', '.git/'))]
    import py_compile
    for f in files:
        try:
            py_compile.compile(f, doraise=True)
        except py_compile.PyCompileError as e:
            failures.append(f'Python 语法错误: {f}: {e}')
    print(f'[Python] {len(files)} 个文件，{len(failures)} 处错误')


def xml_check():
    files = (glob.glob('**/package.xml', recursive=True)
             + glob.glob('**/*.xacro', recursive=True)
             + glob.glob('**/*.sdf', recursive=True))
    files = [f for f in files if not f.startswith(('build/', 'install/', '.git/'))]
    n_bad = 0
    for f in files:
        try:
            ET.parse(f)
        except ET.ParseError as e:
            n_bad += 1
            failures.append(f'XML 解析失败: {f}: {e}')
    print(f'[XML] {len(files)} 个文件，{n_bad} 处错误')


def yaml_check():
    try:
        import yaml
    except ImportError:
        print('[YAML] 未安装 pyyaml，跳过（pip install pyyaml）')
        return
    files = glob.glob('**/*.yaml', recursive=True) + glob.glob('**/*.rviz', recursive=True)
    files = [f for f in files if not f.startswith(('build/', 'install/', '.git/'))]
    n_bad = 0
    for f in files:
        try:
            with open(f) as fh:
                list(yaml.safe_load_all(fh))
        except Exception as e:
            n_bad += 1
            failures.append(f'YAML 解析失败: {f}: {e}')
    print(f'[YAML] {len(files)} 个文件，{n_bad} 处错误')


def pkg_structure():
    """检查 ament_python 包的基本文件是否齐全。"""
    n = 0
    for pkg_xml in glob.glob('*/src/*/package.xml'):
        pkg_dir = os.path.dirname(pkg_xml)
        pkg_name = os.path.basename(pkg_dir)
        tree = ET.parse(pkg_xml)
        build_type = tree.findtext('.//export/build_type', '').strip()
        n += 1
        if build_type == 'ament_python':
            check(os.path.isdir(os.path.join(pkg_dir, pkg_name)),
                  f'{pkg_name}: 缺少 Python 模块目录 {pkg_name}/')
            check(os.path.isfile(os.path.join(pkg_dir, 'resource', pkg_name)),
                  f'{pkg_name}: 缺少 resource/{pkg_name} 标记文件')
            check(os.path.isfile(os.path.join(pkg_dir, 'setup.py')),
                  f'{pkg_name}: 缺少 setup.py')
            # 校验 console_scripts 指向的模块真实存在
            setup_text = open(os.path.join(pkg_dir, 'setup.py')).read()
            for m in re.finditer(r"'([\w.]+):main'", setup_text):
                module = m.group(1)
                path = os.path.join(pkg_dir, module.replace('.', '/') + '.py')
                check(os.path.isfile(path), f'{pkg_name}: 入口模块 {module} 不存在 ({path})')
    print(f'[包结构] 检查了 {n} 个包')


def main():
    print(f'检查目录: {ROOT}\n')
    python_syntax()
    xml_check()
    yaml_check()
    pkg_structure()
    print()
    if failures:
        print(f'发现 {len(failures)} 个问题 ✘')
        for f in failures:
            print('  -', f)
        sys.exit(1)
    print('全部通过 ✔ 可以放心 colcon build 了')


if __name__ == '__main__':
    main()
