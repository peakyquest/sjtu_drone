#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import rclpy
from gazebo_msgs.srv import SpawnEntity


def main(args=None):
    rclpy.init(args=args)
    node = rclpy.create_node('spawn_robot_1')
    cli = node.create_client(SpawnEntity, '/spawn_entity')
    

    content = sys.argv[1]
    namespace = sys.argv[2]
    x_position = sys.argv[3]
    y_position = sys.argv[4]
    z_position = sys.argv[5]

    req = SpawnEntity.Request()
    req.name = namespace
    req.xml = content
    req.robot_namespace = namespace
    req.reference_frame = "world"
    req.initial_pose.position.x = float(x_position)
    req.initial_pose.position.y = float(y_position)
    req.initial_pose.position.z = float(z_position)

    while not cli.wait_for_service(timeout_sec=5.0):
        node.get_logger().info('service not available, waiting again...')

    future = cli.call_async(req)
    rclpy.spin_until_future_complete(node, future)

    if future.result() is not None:
        node.get_logger().info(
            'Result ' + str(future.result().success) + " " + future.result().status_message)
    else:
        node.get_logger().info('Service call failed %r' % (future.exception(),))

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()