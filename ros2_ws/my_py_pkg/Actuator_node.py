#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from example_interfaces.msg import Int32 , Float32


class ActuatorNode(Node): 
    def __init__(self):
        super().__init__("actuator_node") 

        self.latest_distance =None
        self.latest_speed =None

        self.safety_distance =10.0 # in cm
        self.max_distance = 50.0 # in cm
        
        
        self.subscriber_ =self.create_subscription(
            Float32,'/distance', self.callback_distance, 10)
        self.subscriber_ =self.create_subscription(
            Int32,'/cmd_speed', self.callback_speed, 10)
        
   

        self.get_logger().info("Actuator node has been started.")


    def callback_distance(self, msg:Float32):

     self.latest_distance= msg.data
     self.evaluate()


    def callback_speed(self, msg:Int32):
     
          self.latest_speed= msg.data
          self.evaluate()

    def evaluate(self):
     #wait the 2 value arrive 
     if self.latest_speed is None or self.latest_distance is None:
        return

     distance =self.latest_distance
     speed =self.latest_speed

     #safety status

     if distance <= self.safety_distance:
        status = "STOP"
     elif distance >= self.max_distance:
        status = "CLEAR"
     else:
        status = "SLOW"


    # Check if we need an alert

     if distance <= self.safety_distance and speed !=0:
        self.get_logger().info(
           f"ALERT:distance is {distance: .1f}cm but speed is {speed}"
        )

     self.get_logger().info(f"Distance is {distance: .1f}cm   Speed is {speed}"
             )    
     
     self.get_logger().info(
        f'[{status}] Distance: {distance:.1f} cm  -> Speed: {speed}')



def main(args=None):
    rclpy.init(args=args)
    node = ActuatorNode() 
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
