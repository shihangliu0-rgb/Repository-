// 第 02 课：订阅者（C++ 版）。
// 运行: ros2 run talker_listener_cpp listener

#include <memory>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

class Listener : public rclcpp::Node
{
public:
  Listener()
  : Node("listener")
  {
    subscription_ = this->create_subscription<std_msgs::msg::String>(
      "chatter", 10,
      [this](std_msgs::msg::String::SharedPtr msg) {
        RCLCPP_INFO(this->get_logger(), "收到: %s", msg->data.c_str());
      });
    RCLCPP_INFO(this->get_logger(), "Listener 已上线，正在监听 /chatter……");
  }

private:
  rclcpp::Subscription<std_msgs::msg::String>::SharedPtr subscription_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Listener>());
  rclcpp::shutdown();
  return 0;
}
