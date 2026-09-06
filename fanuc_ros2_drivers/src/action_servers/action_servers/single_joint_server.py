#!/usr/bin/env python3
import sys
import os
import rclpy

import dependencies.FANUCethernetipDriver as FANUCethernetipDriver

from dependencies.robot_controller import robot
from fanuc_interfaces.action import SJointPose
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse

FANUCethernetipDriver.DEBUG = False

sys.path.append('./pycomm3/pycomm3')


class sjoint_pose_server(Node):
    def __init__(self):
        super().__init__('sjoint_pose_server')

        self.declare_parameters(
            namespace='',
            parameters=[('robot_ip','172.29.208.0'),
                        ('robot_name','noNAME')] # custom, default
        )

        self.goal = SJointPose.Goal()
        self.bot = robot(self.get_parameter('robot_ip').value)

        self._action_server = ActionServer(self, SJointPose, f"{self.get_parameter('robot_name').value}/single_joint_pose", 
                                        execute_callback = self.execute_callback, 
                                        goal_callback = self.goal_callback,
                                        cancel_callback = self.cancel_callback)

    def goal_callback(self, goal_request):
        """Tells the robot to move a single joint.
        
        Args:
            - goal_request (SJointPose.Goal): msg.joint, corrisponding to a joint, and msg.angle, corrisponding to an angle.

        
        Example:
            .. code-block:: python

                 # Single Joints
                print("Running single joint test")
                self.sin_joint_ac.wait_for_server()
                sjoint_goal = SJointPose.Goal()
                sjoint_goal.joint = 1
                sjoint_goal.angle = 45.0
                future = self.sin_joint_ac.send_goal_async(sjoint_goal, feedback_callback=self.feedback_callback)
                future.add_done_callback(self.goal_response_callback)
        
        
        Returns:
            response (GoalResponse): Either GoalResponse.REJECT or GoalResponse.ACCEPT
        """ 
        self.goal = goal_request 
        
        # Check that it recieved a valid goal
        if self.goal.angle > 179.9 or self.goal.angle < -179.9:
            self.get_logger().info('Invalid request')
            return GoalResponse.REJECT
        if self.goal.joint < 0 or self.goal.joint > 6:
            self.get_logger().info('Invalid request')
            return GoalResponse.REJECT
        else:
            self.get_logger().info('Single Joint goal recieved: '+ str(self.goal))
            return GoalResponse.ACCEPT
                
    def cancel_callback(self, goal_handle):
        """Accept or reject a client request to cancel an action."""
        if self.goal == None:
            self.get_logger().info('No goal to cancel...')
            return CancelResponse.REJECT
        else:
            self.get_logger().info('Received cancel request')
            goal_handle.canceled()
            return CancelResponse.ACCEPT

    async def execute_callback(self, goal_handle):
        try:
            feedback_msg = SJointPose.Feedback()
            feedback_msg.distance_left = self.bot.read_current_joint_position()[self.goal.joint - 1] # starting pose
            
            self.bot.write_joint_position(self.goal.joint, self.goal.angle, blocking=False)

            while self.bot.is_moving():
                # Calculate distance left
                feedback_msg.distance_left -= self.goal.angle
                goal_handle.publish_feedback(feedback_msg) # Send value

                feedback_msg.distance_left = self.bot.read_current_joint_position()[self.goal.joint - 1] # Update cur pos


            goal_handle.succeed()
            result = SJointPose.Result()
            result.success = True
        except:
            goal_handle.canceled()
            result = SJointPose.Result()
            result.success = False
        self.goal = SJointPose.Goal()
        return result

    def destroy(self):
        self._action_server.destroy()
        super().destroy_node()


def main(args=None):
    rclpy.init()

    sjoint_pose_action_server = sjoint_pose_server()

    rclpy.spin(sjoint_pose_action_server)

    sjoint_pose_action_server.destroy()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
