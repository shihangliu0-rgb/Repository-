// 第 01 课：最小节点（C++ 版）。
//
// 运行:
//   ros2 run minimal_node_cpp hello_node

#include <chrono>
#include <memory>

#include "rclcpp/rclcpp.hpp"

using namespace std::chrono_literals;

class HelloNode : public rclcpp::Node
{
public:
  HelloNode()
  : Node("hello_node"), count_(0)
  {
    // 每 1 秒触发一次回调（节点的心跳）
    timer_ = this->create_wall_timer(1s, std::bind(&HelloNode::on_timer, this));
    RCLCPP_INFO(this->get_logger(), "HelloNode 启动！");
  }

private:
  void on_timer()
  {
    ++count_;
    RCLCPP_INFO(
      this->get_logger(),
      "Hello ROS 2! 心跳 #%d (节点名: %s, 命名空间: %s)",
      count_, this->get_name(), this->get_namespace());
  }

  rclcpp::TimerBase::SharedPtr timer_;
  int count_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  auto node = std::make_shared<HelloNode>();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}
