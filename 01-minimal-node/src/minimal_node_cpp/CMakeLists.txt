cmake_minimum_required(VERSION 3.8)
project(minimal_node_cpp)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)

add_executable(hello_node src/hello_node.cpp)
ament_target_dependencies(hello_node rclcpp)

# 把可执行文件安装到 lib/<包名>，这样 `ros2 run` 才能找到它
install(TARGETS
  hello_node
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
