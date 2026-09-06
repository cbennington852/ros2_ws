#!/usr/bin/env python3
import sys
import os
import rclpy

import dependencies.FANUCethernetipDriver as FANUCethernetipDriver

from dependencies.robot_controller import robot
from fanuc_interfaces.action import JointPose
from rclpy.node import Node
from rclpy.action import ActionServer, GoalResponse, CancelResponse

FANUCethernetipDriver.DEBUG = False

sys.path.append('./pycomm3/pycomm3')


class joint_pose_server(Node):
    """Sets the joints
    """
    def __init__(self):
        super().__init__('joint_pose_server')

        self.declare_parameters(
            namespace='',
            parameters=[('robot_ip','172.29.208.0'),
                        ('robot_name','noNAME')] # custom, default
        )

        self.goal = JointPose.Goal()
        self.bot = robot(self.get_parameter('robot_ip').value)

        self._action_server = ActionServer(self, JointPose, f"{self.get_parameter('robot_name').value}/joint_pose", 
                                        execute_callback = self.execute_callback, 
                                        goal_callback = self.goal_callback,
                                        cancel_callback = self.cancel_callback)

    def goal_callback(self, goal_request):
        """Tells the robot to move to a certain joint position. 
        
        Each joint must be joint < 179.9 and joint > -179.9

        Args:
            - goal_request (JointPose.Goal): Takes in joint1-6 parameters. Each are floats.

        Example:
            .. code-block:: python

                print("Running Joint test")
                self.joints_ac.wait_for_server()
                joint_goal = JointPose.Goal()
                # Add all joints
                joint_goal.joint1 = 90.0
                joint_goal.joint2 = 18.0
                joint_goal.joint3 = -41.0
                joint_goal.joint4 = -2.0
                joint_goal.joint5 = -48.0
                joint_goal.joint6 = -148.0
                future = self.joints_ac.send_goal_async(joint_goal, feedback_callback=self.feedback_callback)
                future.add_done_callback(self.goal_response_callback)


        Returns:
            response (GoalResponse): Either GoalResponse.REJECT or GoalResponse.ACCEPT
        """ 
        self.goal = goal_request 
        # FIX!! This is ugly.. Put into a list.any()? Switch is also faster
        # Check that it recieved a valid goal
        if self.goal.joint1 > 179.9 or self.goal.joint1 < -179.9:
            self.get_logger().info('Invalid request')
            return GoalResponse.REJECT
        
        elif self.goal.joint2 > 179.9 or self.goal.joint2 < -179.9:
            self.get_logger().info('Invalid request')
            return GoalResponse.REJECT
        
        elif self.goal.joint3 > 179.9 or self.goal.joint3 < -179.9:
            self.get_logger().info('Invalid request')
            return GoalResponse.REJECT
        
        elif self.goal.joint4 > 179.9 or self.goal.joint4 < -179.9:
            self.get_logger().info('Invalid request')
            return GoalResponse.REJECT
        
        elif self.goal.joint5 > 179.9 or self.goal.joint5 < -179.9:
            self.get_logger().info('Invalid request')
            return GoalResponse.REJECT
        
        elif self.goal.joint6 > 179.9 or self.goal.joint6 < -179.9:
            self.get_logger().info('Invalid request')
            return GoalResponse.REJECT
        else:
            self.get_logger().info('Joint goal recieved: '+ str(self.goal))
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
            feedback_msg = JointPose.Feedback()
            feedback_msg.distance_left = self.bot.read_current_joint_position() # starting pose

            list = [self.goal.joint1,
                    self.goal.joint2,
                    self.goal.joint3,
                    self.goal.joint4, 
                    self.goal.joint5,
                    self.goal.joint6]
            
            self.bot.write_joint_pose(list, blocking=False)

            while self.bot.is_moving():
                # Calculate distance left
                feedback_msg.distance_left[0] -= self.goal.joint1
                feedback_msg.distance_left[1] -= self.goal.joint2
                feedback_msg.distance_left[2] -= self.goal.joint3
                feedback_msg.distance_left[3] -= self.goal.joint4
                feedback_msg.distance_left[4] -= self.goal.joint5
                feedback_msg.distance_left[5] -= self.goal.joint6
                goal_handle.publish_feedback(feedback_msg) # Send value

                feedback_msg.distance_left = self.bot.read_current_joint_position() # Update cur pos

            goal_handle.succeed()
            result = JointPose.Result()
            result.success = True
        except:
            goal_handle.canceled()
            result = JointPose.Result()
            result.success = False
        self.goal = JointPose.Goal() # Reset
        return result

    def destroy(self):
        self._action_server.destroy()
        super().destroy_node()


def main(args=None):
    rclpy.init()

    joint_pose_action_server = joint_pose_server()

    rclpy.spin(joint_pose_action_server)

    joint_pose_action_server.destroy()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
