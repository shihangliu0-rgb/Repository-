cmake_minimum_required(VERSION 3.8)
project(custom_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# 把接口文件交给代码生成器：
# 编译后会自动生成 Python/C++ 等多语言的可导入代码。
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/StudentInfo.msg"
  "srv/SetSpeed.srv"
  "action/Charge.action"
)

ament_package()
