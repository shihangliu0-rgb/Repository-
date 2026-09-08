from setuptools import find_packages, setup

package_name = 'service_demo'

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
    description='第 03 课：服务与 Action 示例',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'add_two_ints_server = service_demo.add_two_ints_server:main',
            'add_two_ints_client = service_demo.add_two_ints_client:main',
            'fibonacci_action_server = service_demo.fibonacci_action_server:main',
            'fibonacci_action_client = service_demo.fibonacci_action_client:main',
        ],
    },
)
