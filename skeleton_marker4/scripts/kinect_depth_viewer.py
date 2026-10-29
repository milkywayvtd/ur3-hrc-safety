#!/usr/bin/env python3
import rospy
import numpy as np
import cv2

from pylibfreenect2 import Freenect2, FrameType, SyncMultiFrameListener, Frame, Registration
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

DMIN = 0.5  # m
DMAX = 4.0  # m

def depth_to_colormap(depth_m, dmin=DMIN, dmax=DMAX):
    d = np.clip(depth_m, dmin, dmax)
    d_norm = ((d - dmin) / (dmax - dmin) * 255.0).astype(np.uint8)
    return cv2.applyColorMap(d_norm, cv2.COLORMAP_JET)

def main():
    rospy.init_node("kinectv2_depth_node", anonymous=True)

    pub_depth = rospy.Publisher("/kinect_depth/colormap", Image, queue_size=1)
    pub_rgb   = rospy.Publisher("/kinect_rgb/registered", Image, queue_size=1)

    bridge = CvBridge()

    fn = Freenect2()
    if fn.enumerateDevices() == 0:
        rospy.logerr("❌ Không thấy Kinect v2")
        return

    serial = fn.getDeviceSerialNumber(0)
    dev = fn.openDevice(serial)

    listener = SyncMultiFrameListener(FrameType.Color | FrameType.Depth)
    dev.setColorFrameListener(listener)
    dev.setIrAndDepthFrameListener(listener)
    dev.start()

    registration = Registration(dev.getIrCameraParams(), dev.getColorCameraParams())
    rospy.loginfo("✅ Kinect streaming (Depth)...")

    saved = False
    rate = rospy.Rate(30)

    try:
        while not rospy.is_shutdown():
            frames = listener.waitForNewFrame()

            color_frame = frames[FrameType.Color]
            depth_frame = frames[FrameType.Depth]

            undistorted = Frame(512, 424, 4)
            registered  = Frame(512, 424, 4)
            registration.apply(color_frame, depth_frame, undistorted, registered)

            # ===== RGB registered (tuỳ bạn xem) =====
            reg = registered.asarray(np.uint8)
            if reg.ndim == 3 and reg.shape[2] == 4:
                rgb_bgr = cv2.cvtColor(reg, cv2.COLOR_BGRA2BGR)
            elif reg.ndim == 3 and reg.shape[2] == 3:
                rgb_bgr = cv2.cvtColor(reg, cv2.COLOR_RGB2BGR)
            else:
                rgb_bgr = reg.copy()
            pub_rgb.publish(bridge.cv2_to_imgmsg(rgb_bgr, encoding="bgr8"))

            # ===== Depth colormap =====
            depth_und = undistorted.asarray(np.float32)  # thường mm
            depth_m = depth_und / 1000.0
            depth_color = depth_to_colormap(depth_m)

            # ghi depth tại tâm ảnh
            cx, cy = 512 // 2, 424 // 2
            X, Y, Z = registration.getPointXYZ(undistorted, cy, cx)
            cv2.circle(depth_color, (cx, cy), 6, (255, 255, 255), -1)
            cv2.putText(depth_color, f"Depth: {Z:.3f} m", (30, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)

            pub_depth.publish(bridge.cv2_to_imgmsg(depth_color, encoding="bgr8"))

            if not saved:
                cv2.imwrite("hinh_3_5_depth.png", depth_color)
                rospy.loginfo("💾 Saved: hinh_3_5_depth.png")
                saved = True

            listener.release(frames)
            rate.sleep()

    finally:
        try:
            dev.stop()
            dev.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()
