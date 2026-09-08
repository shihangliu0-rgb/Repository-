// 第 02 课：发布者（C++ 版）。
// 运行: ros2 run talker_listener_cpp talker

#include <chrono>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/string.hpp"

using namespace std::chrono_literals;

class Talker : public rclcpp::Node
{
public:
  Talker()
  : Node("talker"), count_(0)
  {
    publisher_ = this->create_publisher<std_msgs::msg::String>("chatter", 10);
    timer_ = this->create_wall_timer(1s, std::bind(&Talker::on_timer, this));
    RCLCPP_INFO(this->get_logger(), "Talker 已上线，正在向 /chatter 发布消息……");
  }

private:
  void on_timer()
  {
    auto msg = std_msgs::msg::String();
    msg.data = "Hello from talker #" + std::to_string(count_);
    publisher_->publish(msg);
    RCLCPP_INFO(this->get_logger(), "发布: %s", msg.data.c_str());
    ++count_;
  }

  rclcpp::Publisher<std_msgs::msg::String>::SharedPtr publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
  int count_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<Talker>());
  rclcpp::shutdown();
  return 0;
}
