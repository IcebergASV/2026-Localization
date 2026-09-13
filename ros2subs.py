#!/usr/bin/env python3

import numpy as np
import rclpy
from rclpy.node import Node
from iceberg_msgs.msg import BuoyDetectionArray

from coordConv import build_c2w_matrix, pixel_to_world


class DetectionTransformNode(Node):
    def __init__(self):
        super().__init__('detection_transform_node')

        # --- Camera intrinsics (defaults match the 1080p preset from your script) ---
        self.declare_parameter('fx', 1662.7)
        self.declare_parameter('fy', 1662.7)
        self.declare_parameter('cx', 960.0)
        self.declare_parameter('cy', 540.0)

        # --- Camera pose in world space ---
        self.declare_parameter('cam_x', 0.0)
        self.declare_parameter('cam_y', 0.0)
        self.declare_parameter('cam_z', 0.0)
        self.declare_parameter('pitch_deg', 0.0)
        self.declare_parameter('roll_deg', 0.0)
        self.declare_parameter('yaw_deg', 0.0)

        # --- Whether depth_m from the detection is straight-line distance or planar depth (Zc) ---
        # RealSense get_depth_at_pixel() returns planar depth (Zc), so this defaults to False.
        self.declare_parameter('is_straight_line_dist', False)

        self._build_static_transform()

        self.subscription = self.create_subscription(
            BuoyDetectionArray,
            '/perception/detections',
            self.detection_callback,
            1
        )

        self.get_logger().info("Detection transform node started, waiting for detections...")

    def _build_static_transform(self):
        """Rebuild K and the camera-to-world matrix from current parameters."""
        fx = self.get_parameter('fx').value
        fy = self.get_parameter('fy').value
        cx = self.get_parameter('cx').value
        cy = self.get_parameter('cy').value
        self.K = np.array([
            [fx, 0.0, cx],
            [0.0, fy, cy],
            [0.0, 0.0, 1.0]
        ])

        cam_x = self.get_parameter('cam_x').value
        cam_y = self.get_parameter('cam_y').value
        cam_z = self.get_parameter('cam_z').value
        pitch_deg = self.get_parameter('pitch_deg').value
        roll_deg = self.get_parameter('roll_deg').value
        yaw_deg = self.get_parameter('yaw_deg').value

        self.mworld = build_c2w_matrix(pitch_deg, roll_deg, yaw_deg, (cam_x, cam_y, cam_z))
        self.is_straight_line_dist = self.get_parameter('is_straight_line_dist').value

    def detection_callback(self, msg: BuoyDetectionArray):
        if not msg.detections:
            return

        for det in msg.detections:
            u = det.center_x
            v = det.center_y
            depth = det.depth_m

            if depth <= 0.0:
                # Invalid/no depth reading at that pixel — skip rather than propagate garbage
                self.get_logger().warn(f"Skipping '{det.type}': invalid depth ({depth})")
                continue

            p_cam, p_world = pixel_to_world(
                u, v, depth,
                self.K, self.mworld,
                is_straight_line_dist=self.is_straight_line_dist
            )

            self.get_logger().info(
                f"[{det.type} conf={det.confidence:.2f}] "
                f"cam=({p_cam[0]:.2f}, {p_cam[1]:.2f}, {p_cam[2]:.2f})  "
                f"world=({p_world[0]:.2f}, {p_world[1]:.2f}, {p_world[2]:.2f})"
            )

            # TODO: publish p_world downstream, e.g. as a geometry_msgs/PointStamped
            # or a custom message, once you know what the consumer expects.


def main(args=None):
    rclpy.init(args=args)
    node = DetectionTransformNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()