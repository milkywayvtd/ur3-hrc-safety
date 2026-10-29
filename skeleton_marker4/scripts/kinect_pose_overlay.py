#!/usr/bin/env python3
import rospy
import numpy as np
import cv2
import mediapipe as mp

from pylibfreenect2 import Freenect2, FrameType, SyncMultiFrameListener, Frame, Registration
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

# vài khớp cơ bản
BASIC_JOINTS = [0, 11, 13, 15, 12, 14, 16, 23, 24]
BASIC_EDGES = [
    (11, 13), (13, 15),
    (12, 14), (14, 16),
    (11, 12),
    (11, 23), (12, 24),
    (23, 24),
]

def main():
    rospy.init_node("kinectv2_skeleton_node", anonymous=True)

    pub_img = rospy.Publisher("/kinect_rgb/basic_pose_overlay", Image, queue_size=1)
    bridge = CvBridge()

    # Mediapipe Pose
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(
        static_image_mode=False,
        model_complexity=0,
        enable_segmentation=False,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )

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
    rospy.loginfo("✅ Kinect streaming (Skeleton)...")

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

            reg = registered.asarray(np.uint8)
            if reg.ndim == 3 and reg.shape[2] == 4:
                img_bgr = cv2.cvtColor(reg, cv2.COLOR_BGRA2BGR)
            elif reg.ndim == 3 and reg.shape[2] == 3:
                img_bgr = cv2.cvtColor(reg, cv2.COLOR_RGB2BGR)
            else:
                img_bgr = reg.copy()

            h, w = img_bgr.shape[:2]

            # Mediapipe phải dùng RGB
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            results = pose.process(img_rgb)

            if results.pose_landmarks:
                lms = results.pose_landmarks.landmark

                # vẽ điểm
                for jid in BASIC_JOINTS:
                    lm = lms[jid]
                    if lm.visibility < 0.6:
                        continue
                    x = int(lm.x * (w - 1))
                    y = int(lm.y * (h - 1))
                    cv2.circle(img_bgr, (x, y), 4, (0, 255, 0), -1)

                # vẽ xương
                for a, b in BASIC_EDGES:
                    la = lms[a]
                    lb = lms[b]
                    if la.visibility < 0.6 or lb.visibility < 0.6:
                        continue
                    xa, ya = int(la.x * (w - 1)), int(la.y * (h - 1))
                    xb, yb = int(lb.x * (w - 1)), int(lb.y * (h - 1))
                    cv2.line(img_bgr, (xa, ya), (xb, yb), (0, 0, 255), 2)

            pub_img.publish(bridge.cv2_to_imgmsg(img_bgr, encoding="bgr8"))

            if (not saved) and results.pose_landmarks:
                cv2.imwrite("hinh_3_8_basic_pose.png", img_bgr)
                rospy.loginfo("💾 Saved: hinh_3_8_basic_pose.png")
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
