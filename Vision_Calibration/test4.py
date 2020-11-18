import cv2
import numpy as np

cap = cv2.VideoCapture(0)

while(1):

    # Take each frame
    frame = cap.read()
    frame2 = frame.clone()
    frame3 = frame.clone()

    # Convert BGR to HSV
    hsv_blue = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv_green = hsv.clone() #this will make a copy of the HSV image

    # define range of blue color in HSV
    lower_blue = np.array([110,50,50])
    upper_blue = np.array([130,255,255])

    # define range of blue color in HSV
    lower_green = np.array([50, 100, 100])
    upper_green = np.array([70, 255, 255])

    # Threshold the HSV image to get only blue colors
    mask_blue = cv2.inRange(hsv_blue, lower_blue, upper_blue)
    mask_green = cv2.inRange(hsv_green, lower_green, upper_green)

    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(frame, frame, mask_blue)
    res2 = cv2.bitwise_and(frame2, frame2, mask_green)

    cv2.imshow('frame_blue',frame)
    cv2.imshow('mask_blue',mask_blue)
    cv2.imshow('res_blue',res)

    cv2.imshow('frame_green',frame2)
    cv2.imshow('mask_green',mask_green)
    cv2.imshow('res_green',res2)

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()