#!/usr/bin/env python3
import sys
import os
import rclpy

import dependencies.FANUCethernetipDriver as FANUCethernetipDriver

from dependencies.robot_controller import robot
from fanuc_interfaces.msg import CurCartesian
from rclpy.node import Node

FANUCethernetipDriver.DEBUG = False

sys.path.append('./pycomm3/pycomm3')


class current_cartesian(Node):
    """
    A ROS 2 node that reads and publishes the robot's current Cartesian pose.
    """

    def __init__(self):
        """
        Initializes the node, declares parameters, sets up the robot client,
               and configures the pose publisher and polling timer.
        """
        super().__init__('cur_cart')

        self.declare_parameters(
            namespace='',
            parameters=[('robot_ip','172.29.208.0'),
                        ('robot_name','noNAME')] # custom, default
        )

        self.bot = robot(self.get_parameter('robot_ip').value)
        self.publisher_ = self.create_publisher(CurCartesian, f"{self.get_parameter('robot_name').value}/cur_cartesian", 10)
        timer_period = 0.5
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        """Periodically reads the robot's status and publishes the message.
        Triggered by the main timer loop. Fetches data via the robot driver interface,
        wraps it in a CurCartesian message, and broadcasts it.

        Returns:
            response (CurCartesian): msg.pose tells you the current robot cartesion coords. Returns in the format -> [X, Y, Z, W, P, R]
        """
        msg = CurCartesian()                                          
        msg.pose = self.bot.read_current_cartesian_pose()                                  
        self.publisher_.publish(msg)
        if FANUCethernetipDriver.DEBUG:
        	self.get_logger().info('Publishing: ' % msg.pose)


def main(args=None):
    rclpy.init(args=args)

    publisher = current_cartesian()

    rclpy.spin(publisher)

    publisher.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()
    
