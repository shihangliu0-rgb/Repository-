cmake_minimum_required(VERSION 3.8)
project(learn_gazebo)

find_package(ament_cmake REQUIRED)

# 配置 / 世界 / launch / rviz 配置安装到 share
install(
  DIRECTORY config worlds launch rviz
  DESTINATION share/${PROJECT_NAME}
)

# Python 遥控节点：安装为可执行脚本
install(
  PROGRAMS scripts/teleop_twist.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
