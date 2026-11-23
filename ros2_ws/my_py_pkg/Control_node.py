#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from example_interfaces.msg import Int32 , Float32


class ControlNode(Node): 
    def __init__(self):
        super().__init__("control_node") 
        self.subscriber_ =self.create_subscription(
            Float32,'/distance', self.callback_print_distance, 10)
        self.publisher_  = self.create_publisher(Int32,'/cmd_speed',10)

        #Those the constant that we will need noting that in pahse 5 we will update them to become parameter
        self.safety_distance =10.0 # in cm
        self.max_distance = 50.0 # in cm
        self.max_speed = 200 #PWM

        self.get_logger().info("Control node has been started.")


    def callback_print_distance(self, msg:Float32):

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
    node = ControlNode() 
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
