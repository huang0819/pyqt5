import pyrealsense2.pyrealsense2 as rs
import numpy as np
import cv2
import logging

class DepthCamera:
    def __init__(self):
        logging.info('[DEPTH CAMERA] setup module')
        self.depth_image = None
        self.color_image = None
        self.depth_intrinsic = None

        # Configure depth and color streams
        self.pipeline = rs.pipeline()
        config = rs.config()

        # Get device product line for setting a supporting resolution
        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        pipeline_profile = config.resolve(pipeline_wrapper)
        device = pipeline_profile.get_device()
        device_product_line = str(device.get_info(rs.camera_info.product_line))

        found_rgb = False
        for s in device.sensors:
            if s.get_info(rs.camera_info.name) == 'RGB Camera':
                found_rgb = True
                break
        if not found_rgb:
            logging.info('[DEPTH CAMERA] the demo requires Depth camera with Color sensor')
            exit(0)

        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

        if device_product_line == 'L500':
            config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
        else:
            config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

        # Start streaming
        profile = self.pipeline.start(config)
        # Getting the depth sensor's depth scale (see rs-align example for explanation)

        # align rgb image and depth image
        align_to = rs.stream.color
        self.align = rs.align(align_to)

        depth_sensor = profile.get_device().first_depth_sensor()
        self.depth_scale = depth_sensor.get_depth_scale()

        logging.info('[DEPTH CAMERA] depth scale is: {}'.format(self.depth_scale))

    def read(self):
        # Wait for a coherent pair of frames: depth and color
        frames = self.pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()

        # aligned_depth_frame is a 640x480 depth image
        aligned_frames = self.align.process(frames)
        depth_frame = aligned_frames.get_depth_frame()

        if not depth_frame or not color_frame:
            return None, None

        # Intrinsic & Extrinsic
        if self.depth_intrinsic is None:
            self.depth_intrinsic = depth_frame.profile.as_video_stream_profile().intrinsics

        # Convert images to numpy arrays
        self.color_image = np.asanyarray(color_frame.get_data())
        self.depth_image = np.asanyarray(depth_frame.get_data())

        return self.color_image, self.depth_image

    def save_file(self, file_path):
        # rgb_image = np.copy(self.color_image[:, :, ::-1])
        # depth_image = np.copy(self.depth_image)

        np.savez_compressed(
            file_path,
            rgb_image=self.color_image,
            depth_image=self.depth_image,
            depth_scale=self.depth_scale,
            fx=self.depth_intrinsic.fx,
            fy=self.depth_intrinsic.fy,
            ppx=self.depth_intrinsic.ppx,
            ppy=self.depth_intrinsic.ppy,
        )
