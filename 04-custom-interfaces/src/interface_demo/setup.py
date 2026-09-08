from setuptools import find_packages, setup

package_name = 'interface_demo'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='student',
    maintainer_email='student@example.com',
    description='第 04 课：使用自定义接口的示例节点',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'student_publisher = interface_demo.student_publisher:main',
            'speed_server = interface_demo.speed_server:main',
            'speed_client = interface_demo.speed_client:main',
        ],
    },
)
