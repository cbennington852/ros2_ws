#!/usr/bin/env python3
import sys
import os
import rclpy

import dependencies.FANUCethernetipDriver as FANUCethernetipDriver

from dependencies.robot_controller import robot
from fanuc_interfaces.msg import CurJoints
from rclpy.node import Node

FANUCethernetipDriver.DEBUG = False

sys.path.append('./pycomm3/pycomm3')


class current_joint(Node):
    """
    A ros2 Publisher Node which polls the current joint status. Runs every half a second.
    Returns list of angles at each joint. 
    Access Via msg.joint.
    For example, the angle of joint 1 can be seen by accessing index 0. 
    [0] -> joint 1

    """
    def __init__(self):
        """
        Initializes the node, declares parameters, sets up the robot client,
               and configures the publisher and polling timer.
        """
        super().__init__('curr_joint')

        self.declare_parameters(
            namespace='',
            parameters=[('robot_ip','172.29.208.0'),
                        ('robot_name','noNAME')] # custom, default
        )

        self.bot = robot(self.get_parameter('robot_ip').value)
        self.publisher_ = self.create_publisher(CurJoints, f"{self.get_parameter('robot_name').value}/cur_joints", 10)
        timer_period = 0.5
        self.timer = self.create_timer(timer_period, self.timer_callback)

    def timer_callback(self):
        """Periodically reads the robot's status and publishes the message.
        Triggered by the main timer loop. Fetches data via the robot driver interface,
        wraps it in a CurJoints message, and broadcasts it.

        Returns:
            response (CurJoints): msg.joint is a list of angles at each joint. 
                For example, the angle of joint 1 can be seen by accessing index 0. 
                [0] -> joint 1
        """ 
        msg = CurJoints()                                  
        msg.joints = self.bot.read_current_joint_position()
        self.publisher_.publish(msg)
        if FANUCethernetipDriver.DEBUG:
        	self.get_logger().info('Publishing: ' % msg.joints)


def main(args=None):
    rclpy.init(args=args)

    publisher = current_joint()

    rclpy.spin(publisher)

    publisher.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()
    
