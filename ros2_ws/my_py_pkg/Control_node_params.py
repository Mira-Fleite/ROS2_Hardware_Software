#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from example_interfaces.msg import Int32 , Float32


class ControlNodeParams(Node): 
    def __init__(self):
        super().__init__("control_node_params") 
        self.subscriber_ =self.create_subscription(
            Float32,'/distance', self.callback_print_distance, 10)
        self.publisher_  = self.create_publisher(Int32,'/cmd_speed',10)

       
        self.declare_parameter('safety_distance', 10.0)
        self.declare_parameter('max_distance', 50.0)
        self.declare_parameter('max_speed', 200)

        self.get_logger().info("Control node has been started.")


    def callback_print_distance(self, msg:Float32):
     self.safety_distance = self.get_parameter('safety_distance').value
     self.max_distance = self.get_parameter('max_distance').value
     self.max_speed = self.get_parameter('max_speed').value

     distance =msg.data

     if distance <= self.safety_distance:
        speed = 0

     elif distance >= self.max_distance:
        speed = self.max_speed

     else:
        ratio =(distance -self.safety_distance)/(self.max_distance -self.safety_distance)

        speed =int(ratio*self.max_speed)

     speed_msg=Int32()
     speed_msg.data= speed

     self.publisher_.publish(speed_msg)


     self.get_logger().info(
        f'Distance: {distance:.1f} cm  -> Speed: {speed}')



def main(args=None):
    rclpy.init(args=args)
    node = ControlNodeParams() 
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
