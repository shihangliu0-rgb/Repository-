from setuptools import find_packages, setup

package_name = 'minimal_node'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        # 必须安装这两样，ros2 工具链才能索引到本包
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='student',
    maintainer_email='student@example.com',
    description='第 01 课：最小 ROS 2 节点（Python 版）',
    license='Apache-2.0',
    tests_require=['pytest'],
    # console_scripts：把 Python 函数注册成可用 `ros2 run` 启动的可执行文件
    entry_points={
        'console_scripts': [
            'hello_node = minimal_node.hello_node:main',
        ],
    },
)
