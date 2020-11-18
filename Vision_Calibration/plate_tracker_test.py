import cv2
import numpy as np
import math

from dataStructures import Object



def track_plate(frame, colour):
    """
    Finds the plate with the specified central colour then crops it from the original frame
    """
    # range for red ball
    #lower_yellow = np.array([30,150,150])
    #upper_yellow = np.array([37,255,255])
    # lower_yellow = np.array([49, 150, 150]) #actually green
    # upper_yellow = np.array([51, 255, 255]) #actually green
    #lower_yellow = np.array([130, 100, 100])#actually pink
    #upper_yellow = np.array([171, 204, 255])#actually pink

    # Select which team to track
    if (colour == "yellow"):
        lower_boundary = np.array([30, 150, 150])
        upper_boundary = np.array([37, 255, 255])

    elif (colour == "blue"):
        lower_boundary = np.array([80, 100, 200])
        upper_boundary = np.array([100, 255, 250])

    # The mask contains the pixels which are in the colour boundary
    mask = cv2.inRange(frame, lower_boundary, upper_boundary)
    cv2.imshow(colour,mask)

    # dilate the image to make contours bigger, then close it to improve recognition
    kernel_dilate = np.ones((2, 2), np.uint8)
    kernel_close = np.ones((5, 5), np.uint8)
    dilate = cv2.dilate(mask, kernel_dilate)
    close = cv2.morphologyEx(dilate, cv2.MORPH_CLOSE, kernel_close)
    #cv2.imshow("team_mask", close)


    # find all groupings of pixels found by mask
    _, contours, hierarchy = cv2.findContours(close, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) #original
    # find area of all contours
    areas = [cv2.contourArea(c) for c in contours]

    robot_1 = Object(0, 0, 0, 0, 0)
    robot_2 = Object(0, 0, 0, 0, 0)

    if (areas != []):
        if (len(areas) == 1):
            largest_index = np.argmax(areas)
            contour = contours[largest_index]

            (float_x, float_y), radius = cv2.minEnclosingCircle(contour)
            #center = (int(x), int(y))
            radius = int(radius)

            if (int(float_x) < 30):
                x = 30
            elif (int(float_x) > 1250):
                x = 1250
            else:
                x = int(float_x)

            if (int(float_y) < 30):
                y = 30
            elif (int(float_y) > 1250):
                y = 1050
            else:
                y = int(float_y)

            center = (x, y)

            #robot = frame[center[1]-30:center[1]+30, center[0]-30:center[0]+30]
            robot = Object(x, y, 0, 0, 0)
            return(robot, robot)


        if (len(areas) >= 2):
            largest_2_indices = np.argpartition(areas, 1)[-2:]
            #largest_contour = contours[np.argmax(areas)]

            # Get the contours for the two robots of the team
            contour_1 = contours[largest_2_indices[0]]
            contour_2 = contours[largest_2_indices[1]]


            (float_x_1, float_y_1), radius_1 = cv2.minEnclosingCircle(contour_1)
            (float_x_2, float_y_2), radius_2 = cv2.minEnclosingCircle(contour_2)

            #center_1 = (int(x_1),int(y_1))
            radius_1 = int(radius_1)
            #center_2 = (int(x_2),int(y_2))
            radius_2 = int(radius_2)

            #cv2.circle(frame, center_1, radius_1, (0, 0, 255), 1)
            #cv2.circle(frame, center_2, radius_2, (0, 0, 255), 1)

            if (int(float_x_1) < 30):
                x_1 = 30
            elif (int(float_x_1) > 1250):
                x_1 = 1250
            else:
                x_1 = int(float_x_1)

            if (int(float_y_1) < 30):
                y_1 = 30
            elif (int(float_y_1) > 1250):
                y_1 = 1050
            else:
                y_1 = int(float_y_1)

            center_1 = (x_1, y_1)

            #############################

            if (int(float_x_2) < 30):
                x_2 = 30
            elif (int(float_x_2) > 1250):
                x_2 = 1250
            else:
                x_2 = int(float_x_2)

            if (int(float_y_2) < 30):
                y_2 = 30
            elif (int(float_y_2) > 1250):
                y_2 = 1050
            else:
                y_2 = int(float_y_2)

            center_2 = (x_2, y_2)

            #crop the part of the image containing the robot from the yellow team
            #robot_1 = frame[center_1[1]-30:center_1[1]+30, center_1[0]-30:center_1[0]+30]
            #robot_2 = frame[center_2[1]-30:center_2[1]+30, center_2[0]-30:center_2[0]+30]
            robot_1 = Object(center_1[0], center_1[1], 0, 0, 0)
            robot_2 = Object(center_2[0], center_2[1], 0, 0, 0)

            #cv2.imshow("robot_1", robot_1)
            #cv2.imshow("robot_2", robot_2)


            return (robot_1, robot_2)

    else:
        #cropped_frame = frame[240:300, 240:300]
        robot_1 = Object(270, 270, 0, 0, 0)
        robot_2 = Object(270, 270, 0, 0, 0)
        #return (cropped_frame, cropped_frame)
        return (robot_1, robot_2)

    # If cannot find two robots, return some dummy data
    # Should figure out something better for the final version
    # cropped_frame = frame[240:300, 240:300]

    #return (cropped_frame, cropped_frame)


def colour_density(robot_frame):
    """
    The function determines the dominating colour on the plate.
    """


    pink_mask = cv2.inRange(robot_frame, np.array([130, 100, 100]), np.array([171, 204, 255]))
    green_mask = cv2.inRange(robot_frame,  np.array([45,  80, 180]), np.array([57, 255, 255]))
    
    #count the number of green and pink pixels
    pink = np.count_nonzero(pink_mask)
    green = np.count_nonzero(green_mask)

    main_colour = None

    # compare the counts of the colours
    if(pink > green):
        main_colour = "pink"
        #print(main_colour)
    else:
        main_colour = "green"

        
    return main_colour


def track_orientation_dot(robot_frame, colour):
    """
    Finds the single dot on the plate, based on its colour
    """

    orientation_dot = Object(0, 0, 0, 0, 0)

    #cv2.imshow("robot frame", robot_frame)
    #if the main colour is pink, search for green
    if(colour == "pink"):
        lower_boundary = np.array([49, 150, 150])
        upper_boundary = np.array([51, 255, 255])
    #if the main colour is green, search for pink
    elif(colour == "green"):
        lower_boundary = np.array([130, 100, 100])
        upper_boundary = np.array([171, 204, 255])

    # mask contains the pixels which are in the colour boundary
    mask = cv2.inRange(robot_frame, lower_boundary, upper_boundary)

    # dilate the image to make contours bigger, then close it to improve recognition
    kernel = np.ones((2,2), np.uint8)
    kernel2 = np.ones((5,5),np.uint8)
    frame_mask = cv2.dilate(mask, kernel)
    closing = cv2.morphologyEx(frame_mask, cv2.MORPH_CLOSE, kernel2)

    # find all groupings of pixels found by mask
    im2, contours, hierarchy = cv2.findContours(closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    #cv2.imshow("track_orientation_dot", mask)
    # find area of all contours
    areas = [cv2.contourArea(c) for c in contours]

    if areas != []:
        largest_contour = contours[np.argmax(areas)]
        (x,y),radius = cv2.minEnclosingCircle(largest_contour)
        #if (colour == "pink"):
            #print "(x,y) = " +str((x,y))
        #center = (int(x),int(y))
        #radius = int(radius)
        #cv2.circle(robot_frame, center, radius, (0,255,0), 2)

        orientation_dot = Object(x, y, 0, 0, 0)
        return orientation_dot
    else:
        return orientation_dot

def orientation(team_dot, orientation_dot):
    """
    Calculates the orientation of the robot using the slope of the line,
    connecting the team marker dot and the orientation dot
    """
    orient_dot = (team_dot.x -30 + orientation_dot.x, team_dot.y - 30 + orientation_dot.y)
    slope = ((team_dot.y-orient_dot[1]) , (team_dot.x - orient_dot[0]))
    slope_angle = math.atan2(slope[0],slope[1])
    #print (slope_angle)

    #rotate the orientation dot around the center dot by 30 degrees
    #v = ((team_dot.x - orient_dot[0]), (team_dot.y - orient_dot[1]))
    v = ((orient_dot[0] - team_dot.x), (orient_dot[1] - team_dot.y))
    xcos = v[0] * math.cos(-145 * math.pi / 180)
    ysin = v[1] * math.sin(-145 * math.pi / 180)
    xsin = v[0] * math.sin(-145 * math.pi / 180)
    ycos = v[1] * math.cos(-145 * math.pi / 180)
    v_1 = (xcos - ysin, xsin - ycos)
    #v_2 = (v_1[0] + orient_dot[0], v_1[1] + orient_dot[1])
    v_2 = (v_1[0] + team_dot.x, v_1[1] + team_dot.y)

    # new one
    if team_dot.x > orient_dot[0]:
        mag = 1
    else:
        mag = -1
    slope_angle_prime = slope_angle - math.radians(35)
    new_point = (team_dot.x +  20* math.cos( slope_angle_prime),team_dot.y + 20 * math.sin(slope_angle_prime))
    new_point = (int(new_point[0]),int(new_point[1]))


    print("--------------")
    print(orient_dot)
    print(v_2)

    # return ((team_dot.x, team_dot.y), (int(v_2[0]), int(v_2[1])))
    return ((team_dot.x, team_dot.y), new_point)


def preProcess(frame):
        #dst = cv2.remap(img,mapx,mapy,cv2.INTER_LINEAR)
        kernel = np.ones((2,2), np.uint8)
        opened = cv2.morphologyEx(frame, cv2.MORPH_OPEN, kernel)
        dilated = cv2.dilate(opened, kernel, iterations = 3)
        return dilated

def main():

    # Create the datastructures which will store the information about the robots
    yellow_robot_1 = Object(0, 0, 0, 0, 0)
    yellow_robot_2 = Object(0, 0, 0, 0, 0)
    blue_robot_1 = Object(0, 0, 0, 0, 0)
    blue_robot_2 = Object(0, 0, 0, 0, 0)

    cap = cv2.VideoCapture(0)

    while(1):
         # Take each frame
        _, frame = cap.read()
        #cv2.imshow("rgb", frame)

        #Blur the frame to make colours more uniform
        preprocessed = preProcess(frame)
        cv2.imshow("preprocessed", preprocessed)

        # Convert BGR to HSV
        #hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hsv_frame = cv2.cvtColor(preprocessed, cv2.COLOR_BGR2HSV)
        #cv2.imshow("hsv", hsv_frame)
        #time.sleep(1)

        ###########################################
        pink_mask = cv2.inRange(hsv_frame, np.array([130, 100, 100]), np.array([171, 204, 255]))
        green_mask = cv2.inRange(hsv_frame, np.array([45,  80, 180]), np.array([57, 255, 255]))
        cv2.imshow('pink',pink_mask)
        cv2.imshow('green',green_mask)
        #####################################

        # find the plate
        yellow_plates = track_plate(hsv_frame, "yellow")
        yellow_robot_1 = yellow_plates[0]
        yellow_robot_2 = yellow_plates[1]

        blue_plates = track_plate(hsv_frame, "blue")
        blue_robot_1 = blue_plates[0]
        blue_robot_2 = blue_plates[1]
        #print(plate_1.shape)
        #cv2.imshow('plate_1', plate_1)
        #cv2.imshow('plate_2', plate_2)

        yellow_robot_1_frame = hsv_frame[yellow_robot_1.y-30:yellow_robot_1.y+30, yellow_robot_1.x-30:yellow_robot_1.x+30]
        yellow_robot_2_frame = hsv_frame[yellow_robot_2.y-30:yellow_robot_2.y+30, yellow_robot_2.x-30:yellow_robot_2.x+30]

        blue_robot_1_frame = hsv_frame[blue_robot_1.y-30:blue_robot_1.y+30, blue_robot_1.x-30:blue_robot_1.x+30]
        blue_robot_2_frame = hsv_frame[blue_robot_1.y-30:blue_robot_1.y+30, blue_robot_1.x-30:blue_robot_1.x+30]


        yellow_1_main_colour = colour_density(yellow_robot_1_frame)
        yellow_2_main_colour = colour_density(yellow_robot_2_frame)

        blue_1_main_colour = colour_density(blue_robot_1_frame)
        blue_2_main_colour = colour_density(blue_robot_2_frame)


        yellow_1_orientation_dot = track_orientation_dot(yellow_robot_1_frame, yellow_1_main_colour)
        print("orientation:")
        print(yellow_1_orientation_dot.x, yellow_1_orientation_dot.y)
        yellow_2_orientation_dot = track_orientation_dot(yellow_robot_2_frame, yellow_2_main_colour)
        print("orientation-dot 2:")
        print(yellow_2_orientation_dot.x, yellow_2_orientation_dot.y)
        blue_1_orientation_dot = track_orientation_dot(blue_robot_1_frame, blue_1_main_colour)
        blue_2_orientation_dot = track_orientation_dot(blue_robot_2_frame, blue_2_main_colour)
        #cv2.imshow("orientation_dot_1", final_frame_1)


        cv2.circle(frame, (int(yellow_1_orientation_dot.x), int(yellow_1_orientation_dot.y)), 5, (0, 0, 0), 2)
        cv2.circle(frame, (int(yellow_robot_1.x -30 + yellow_2_orientation_dot.x), int(yellow_robot_1.y -30 + yellow_2_orientation_dot.y)), 5, (255, 255, 255), 2)



        #final_frame_2 = track_orientation_dot(plate_2, main_colour_2)
        #cv2.imshow("orientation_dot_2", final_frame_2)
        yellow_angle_1 = orientation(yellow_robot_1, yellow_1_orientation_dot)
        yellow_angle_2 = orientation(yellow_robot_2, yellow_2_orientation_dot)

        blue_angle_1 = orientation(blue_robot_1, blue_1_orientation_dot)
        blue_angle_2 = orientation(blue_robot_2, blue_2_orientation_dot)

        #Draw everything on frame
        cv2.rectangle(frame, (yellow_robot_1.x-30, yellow_robot_1.y-30), (yellow_robot_1.x+30, yellow_robot_1.y+30), (255, 255, 0))
        cv2.rectangle(frame, (yellow_robot_2.x-30, yellow_robot_2.y-30), (yellow_robot_2.x+30, yellow_robot_2.y+30), (255, 255, 0))

        cv2.rectangle(frame, (blue_robot_1.x-30, blue_robot_1.y-30), (blue_robot_1.x+30, blue_robot_1.y+30), (255, 0, 0))
        cv2.rectangle(frame, (blue_robot_2.x-30, blue_robot_2.y-30), (blue_robot_2.x+30, blue_robot_2.y+30), (255, 0, 0))


        cv2.line(frame, yellow_angle_1[0], yellow_angle_1[1], (255, 255, 0), 2)
        cv2.line(frame, yellow_angle_2[0], yellow_angle_2[1], (255, 255, 0), 2)

        cv2.line(frame, blue_angle_1[0], blue_angle_1[1], (255, 0, 0), 2)
        cv2.line(frame, blue_angle_2[0], blue_angle_2[1], (255, 0, 0), 2)


        cv2.imshow("final_frame", frame)


        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            break

    cv2.destroyAllWindows()




if __name__ == '__main__':
    main()
