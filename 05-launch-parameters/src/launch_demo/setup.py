import os
from glob import glob

from setuptools import find_packages, setup

package_name = 'launch_demo'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        # 关键：把 launch 文件和参数 YAML 安装到 share 目录，
        # 这样 `ros2 launch launch_demo xxx.launch.py` 才能找到它们。
        (os.path.join('share', package_name, 'launch'),
            glob(os.path.join('launch', '*.launch.py'))),
        (os.path.join('share', package_name, 'config'),
            glob(os.path.join('config', '*.yaml'))),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='student',
    maintainer_email='student@example.com',
    description='第 05 课：Launch 文件与参数',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'talker = launch_demo.talker:main',
            'listener = launch_demo.listener:main',
        ],
    },
)
