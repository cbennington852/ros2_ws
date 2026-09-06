#!/usr/bin/env python3
import sys
import os
import rclpy

import dependencies.FANUCethernetipDriver as FANUCethernetipDriver

from dependencies.robot_controller import robot
from fanuc_interfaces.msg import CurGripper
from rclpy.node import Node

FANUCethernetipDriver.DEBUG = False

sys.path.append('./pycomm3/pycomm3')


class check_grip(Node):
    """
    Tells you what the current status of the gripper hand is.
    """
    def __init__(self):
        """
        Initializes the node, declares parameters, sets up the robot client,
               and configures the pose publisher and polling timer.
        """
        super().__init__('grip_pub')

        self.declare_parameters(
            namespace='',
            parameters=[('robot_ip','172.29.208.0'),
                        ('robot_name','noNAME')] # custom, default
        )

        self.bot = robot(self.get_parameter('robot_ip').value)
        self.publisher_ = self.create_publisher(CurGripper, f"{self.get_parameter('robot_name').value}/grip_status", 10)
        timer_period = 0.5
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        """Periodically reads the robot's status and publishes the message.
        Triggered by the main timer loop. Fetches data via the robot driver interface,
        wraps it in a CurGripper message, and broadcasts it.

        Returns:
            response (CurGripper): msg.open tells you if the gripper is open.
        """
        msg = CurGripper()                               
        msg.open = bool(self.bot.schunk_gripper_status())                      
        self.publisher_.publish(msg)
        # if FANUCethernetipDriver.DEBUG:
        # 	self.get_logger().info('Publishing: ' % msg.open)


def main(args=None):
    rclpy.init(args=args)

    publisher = check_grip()

    rclpy.spin(publisher)

    publisher.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()
    

