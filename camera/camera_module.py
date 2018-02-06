#  -*- coding: utf-8 -*-
import cv2


cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)
cap.set(1, 10.0)
print(cap.isOpened())
