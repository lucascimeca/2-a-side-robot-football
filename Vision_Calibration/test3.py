import cv2
import numpy as np

cap = cv2.VideoCapture(0)

while(1):

    # Take each frame
    _, frame = cap.read()


    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV
    lower_blue = np.array([110,50,50])
    upper_blue = np.array([130,255,255])

    lower_red = np.array([-10, 100, 100])
    upper_red = np.array([10, 255, 255])

    lower_white = np.array([-10, 0, 255])
    upper_white = np.array([10, 0, 255])
    #lower_red = np.array([110,50,50])
    #upper_red = np.array([130,255,255])
    # Threshold the HSV image to get only blue colors
    red_mask = cv2.inRange(hsv, lower_red, upper_red)
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    white_mask = cv2.inRange(hsv, lower_white, upper_white)
    mask = red_mask + blue_mask + white_mask
    #mask2 = cv2.inRange(hsv, lower_red, upper_red)

    # Bitwise-AND mask and original image
    res = cv2.bitwise_and(frame,frame, mask= mask)
    #res2 = cv2.bitwise_and(frame,frame, mask= mask2)
    cv2.imshow('frame',frame)
    cv2.imshow('mask',mask)
    cv2.imshow('res',res)

    #cv2.imshow('frame',frame)
    #cv2.imshow('mask2',mask2)
    #cv2.imshow('res',res2)
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()