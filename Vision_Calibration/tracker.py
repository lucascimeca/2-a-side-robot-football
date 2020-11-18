import cv2
import numpy as np
import bottleneck as bn

import time

cap = cv2.VideoCapture(0)

def get_contour_corners(contour):
    """ Returns exact corners for the plate given a contour"""

    if contour is not None:
        rectangle = cv2.minAreaRect(contour)
        box =  box = cv2.cv.BoxPoints(rectangle)        #Finds four vertices of rectangle from above rectangle
        return np.int0(box)                         



while(1):

    # Take each frame
    _, frame = cap.read()


    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)


    width = np.size(frame, 1) #here is why you need numpy!  (remember to "import numpy as np")
    height = np.size(frame, 0)
    print(width)
    print(height)

    #time.sleep(4)

    # define range of blue color in HSV
    lower_plate_blue = np.array([80,120,200])
    upper_plate_blue = np.array([95,160,250])

    lower_blue = np.array([110,50,50])
    upper_blue = np.array([130,255,255])

    lower_red = np.array([-10, 100, 100])
    upper_red = np.array([5, 255, 255])
    # mean is 32,214,214
    lower_yellow = np.array([30,150,150])
    upper_yellow = np.array([35,255,255])

    #Possible green color for the plate. Need to Test
    lower_green = np.array([46,180, 100])
    upper_green = np.array([58, 255, 255])

    lower_pink = np.array([130, 100, 100])       #169,
    upper_pink = np.array([171, 204, 255]) 
    #lower_white = np.array([-10, 0, 255])
    #upper_white = np.array([10, 0, 255])

    #lower_red = np.array([110,50,50])   
    #upper_red = np.array([130,255,255])
    # Threshold the HSV image to get only blue colors
    red_mask = cv2.inRange(hsv, lower_red, upper_red)
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    green_mask = cv2.inRange(hsv, lower_green, upper_green)
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
    pink_mask = cv2.inRange(hsv, lower_pink, upper_pink)
    blue_plate_mask = cv2.inRange(hsv, lower_plate_blue, upper_plate_blue)
    #white_mask = cv2.inRange(hsv, lower_white, upper_white)
    #mask = red_mask
    mask = blue_plate_mask
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
    kernel = np.ones((2,2), np.uint8)
    kernel2 = np.ones((5,5),np.uint8)
    frame_mask = cv2.dilate(mask, kernel)   #, iterations=adjustments['erode'])
    cv2.imshow("dilate", frame_mask)
    closing = cv2.morphologyEx(frame_mask, cv2.MORPH_CLOSE, kernel2)
    cv2.imshow("closing", closing)



    im2, contours, hierarchy = cv2.findContours(closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    areas = []  
    areas = [cv2.contourArea(c) for c in contours]
    print(areas)
    if areas != []:
        largest_contour = contours[np.argmax(areas)]
        #areas = bn.argpartsort((areas),2)
        if len(areas) >= 2:
            areas = np.argpartition([-x for x in areas],1)
            largest_contour = contours[areas[0]]
            seccond_contour = contours[areas[1]]

            #min_circle = cv2.minEnclosingCircle(largest_contour)
            (x,y),radius = cv2.minEnclosingCircle(largest_contour)
            (x2,y2),radius2 = cv2.minEnclosingCircle(seccond_contour)
            center = (int(x),int(y))
            center2 = (int(x2),int(y2))
            radius = int(radius)
            radius2 = int(radius2)
            #print(center)
            #print(radius)
            print "(x,y)largest_contour = "
            print x,y
            #contour_frame = np.zeros((480,640),)
            cv2.circle(frame, center,radius,(0,255,0),2)
            #cv2.circle(frame, center2,radius2,(0,0,255),2)
            cv2.imshow("bla", frame)




    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()