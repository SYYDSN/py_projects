#  -*- coding: utf-8 -*-
import cv2


cap = cv2.VideoCapture('/home/walle/视频/VID_20170213_141915.mp4')
cv2.waitKey(0)
print(cap.isOpened())