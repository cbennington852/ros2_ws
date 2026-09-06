#!/usr/bin/env python3
import sys
import os
import rclpy

import dependencies.FANUCethernetipDriver as FANUCethernetipDriver

from dependencies.robot_controller import robot
from fanuc_interfaces.srv import Mount
from rclpy.node import Node

FANUCethernetipDriver.DEBUG = False

sys.path.append('./pycomm3/pycomm3')


class go_mount(Node):
    """
    set the joints to be in a 'mount' position for tooling. 
        This is for CRX10's and will most likely be removed from this API

    Returns a responce. Can return either. 
    responce.success = True 
    responce.success = False
    """

    def __init__(self):
        super().__init__('mount_srv')

        self.declare_parameters(
            namespace='',
            parameters=[('robot_ip','172.29.208.0'),
                        ('robot_name','noNAME')] # custom, default
        )

        self.bot = robot(self.get_parameter('robot_ip').value)
        self.srv = self.create_service(Mount, f"{self.get_parameter('robot_name').value}/go_mount", self.service_callback)

    def service_callback(self, request, response):
        """
        Sets the joints into a mount position. 

        Args:
            request (None): Not used.
            response (Any): The success parameter is set to True or False.

        Returns:
            response (Any): The success parameter is set to True or False.
        """
        self.bot.set_joints_to_mount_position(blocking=False)
        try:
            while True: # Verify that it actually completed
                curPos = self.bot.read_current_joint_position()
                if (abs(curPos[0] - 1.0) <= 2 and
                    abs(curPos[1] - 58.0) <= 2 and
                    abs(curPos[2] - -12.0) <= 2 and
                    abs(curPos[3] - -2.0) <= 2 and
                    abs(curPos[4] - 11.0) <= 2 and
                    abs(curPos[5] - -6.0) <= 2):
                    break
        except:
            response.success = False  # If here, there was some kind of error      
        else:
            self.get_logger().info('Going to mount position')
            response.success = True   # Otherwise, evrything went well
        if FANUCethernetipDriver.DEBUG:
            self.get_logger().info('Incoming request result: ',response.success)

        return response


def main(args=None):
    rclpy.init(args=args)

    publisher = go_mount()

    rclpy.spin(publisher)

    publisher.destroy_node()
    rclpy.shutdown()
    
if __name__ == '__main__':
    main()
    
