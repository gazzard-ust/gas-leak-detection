#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
import cv2
import numpy as np
import subprocess
import io
from PIL import Image

class ImagePublisher(Node):
    def __init__(self):
        super().__init__('image_publisher')
        self.publisher = self.create_publisher(CompressedImage, '/image/compressed', 1)

        # Increased FPS: 0.033s = ~30 FPS (changed from 0.1s = 10 FPS)
        self.timer = self.create_timer(0.033, self.publish_image)


        # Try picamera2 first (for libcamera systems)
        self.use_picamera2 = False
        self.use_libcamera_cmd = False

        try:
            from picamera2 import Picamera2
            self.get_logger().info("Using picamera2 for camera access")
            self.picam2 = Picamera2()
            config = self.picam2.create_preview_configuration(
                main={"size": (640, 480), "format": "RGB888"}
            )
            self.picam2.configure(config)
            self.picam2.start()
            self.use_picamera2 = True
            self.get_logger().info("Picamera2 initialized successfully")
        except Exception as e:
            self.get_logger().warn(f"Picamera2 failed ({e}), trying libcamera commands...")

            # Try libcamera-jpeg or rpicam-jpeg command
            self.libcamera_cmd = None
            try:
                # Check for rpicam-jpeg (newer)
                result = subprocess.run(['which', 'rpicam-jpeg'],
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    self.libcamera_cmd = 'rpicam-jpeg'
                else:
                    # Check for libcamera-jpeg (older)
                    result = subprocess.run(['which', 'libcamera-jpeg'],
                                          capture_output=True, text=True, timeout=2)
                    if result.returncode == 0:
                        self.libcamera_cmd = 'libcamera-jpeg'

                if self.libcamera_cmd:
                    self.use_libcamera_cmd = True
                    self.get_logger().info(f"Using {self.libcamera_cmd} command for camera access")
                else:
                    raise Exception("No libcamera commands found")
            except Exception as e2:
                self.get_logger().warn(f"libcamera commands failed ({e2}), trying OpenCV...")
                self.use_picamera2 = False
                self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.cap.set(cv2.CAP_PROP_FPS, 30)

                if not self.cap.isOpened():
                    self.get_logger().error("Failed to open camera with OpenCV")
                    return

        self.get_logger().info("Image Publisher Node Started")

    def publish_image(self):
        if self.use_picamera2:
            try:
                frame = self.picam2.capture_array()
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                # Save one test frame on first capture so we can check colors locally
                if not hasattr(self, '_saved_test'):
                    cv2.imwrite('/tmp/test_frame.jpg', frame)
                    self.get_logger().info(
                        f"Saved test frame to /tmp/test_frame.jpg | "
                        f"shape={frame.shape} dtype={frame.dtype} "
                        f"pixel[0,0]={frame[0,0]}"
                    )
                    self._saved_test = True
            except Exception as e:
                self.get_logger().error(f"Failed to capture from picamera2: {e}")
                return
        elif self.use_libcamera_cmd:
            try:
                # Capture a single frame using libcamera-jpeg or rpicam-jpeg
                result = subprocess.run([
                    self.libcamera_cmd, '-o', '-', '-t', '1', '--width', '640', '--height', '480', '-n'
                ], capture_output=True, timeout=2)

                if result.returncode == 0:
                    # Convert JPEG bytes to numpy array
                    img = Image.open(io.BytesIO(result.stdout))
                    frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                else:
                    self.get_logger().error("Failed to capture from libcamera-jpeg")
                    return
            except Exception as e:
                self.get_logger().error(f"libcamera-jpeg error: {e}")
                return
        else:
            ret, frame = self.cap.read()
            if not ret:
                self.get_logger().error("Lost camera connection. Retrying...")
                self.cap.release()
                self.cap = cv2.VideoCapture(0)
                return

        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        msg = CompressedImage()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.format = "jpeg"
        msg.data = np.array(buffer).tobytes()

        self.publisher.publish(msg)
        self.get_logger().info("Published compressed image")

    def destroy_node(self):
        if self.use_picamera2:
            self.picam2.stop()
        elif not self.use_libcamera_cmd:
            self.cap.release()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = ImagePublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Image Publisher Shutdown")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()