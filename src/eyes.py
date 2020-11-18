import time
import math
import cv2
import numpy as np
from scipy import stats
from base import *
import glob
import copy
import yaml

# Note all references to x and y coordinates in this file are in pixels

class Eye:
    # This will run in parallel to BendingUnit and
    # the planner
    keepLooking = True    
    didBeliefChange = True
    #0-crop 1-red   2-yellow    3-blue  4-pink  5-green
    changeThresh = 0
    calibActive = False
    calib = yaml.load(file('vision.yaml').read())
    #[HueL,SatL,ValL],[HueU,SatU,ValU]
    # redRange    = np.array([[  0,200,161],[  8,255,255]])
    # redLower    = np.array([[170,230,161],[180,255,255]])
    # yellowRange = np.array([[ 30,170,138],[ 36,255,255]])
    # blueRange   = np.array([[ 75,114,121],[100,255,255]])
    # pinkRange   = np.array([[130,113,127],[173,255,255]])
    # greenRange  = np.array([[ 49,171,157],[ 67,255,255]])
    redRange    = np.array(calib['redRange'])
    redLower    = np.array(calib['redLower'])
    yellowRange = np.array(calib['yellowRange'])
    blueRange   = np.array(calib['blueRange'])
    pinkRange   = np.array(calib['pinkRange'])
    greenRange  = np.array(calib['greenRange'])



    def __init__(self, beliefs, started=None, beliefsUpdatedEvent=None):
        # We pass the BendingUnit Object in here as 'me'

        self.beliefs = beliefs
        self.beliefsUpdatedEvent = beliefsUpdatedEvent

        # started event is simply to give Eye the change to perform its preprocessing
        self.started = started

    def getBeliefs(self):
        return self.beliefs

    def startLooking(self):
        # positions of last 5 balls
        last_balls = [Ball(0,0,0,0,0),Ball(0,0,0,0,0),Ball(0,0,0,0,0),Ball(0,0,0,0,0),Ball(0,0,0,0,0)]
        
        # These are pointers to the persistent instances of robots on the field
        yellow_robot_green = self.beliefs.colourAssignments['yellow']['green']
        last_yellow_robot_green = []
        yellow_robot_pink = self.beliefs.colourAssignments['yellow']['pink']
        last_yellow_robot_pink = []
        blue_robot_green = self.beliefs.colourAssignments['blue']['green']
        last_blue_robot_green = []
        blue_robot_pink = self.beliefs.colourAssignments['blue']['pink']
        last_blue_robot_pink = []


        cap = cv2.VideoCapture(0)
        cap.set(10,0.20)      #brightness
        cap.set(11,0.50)      #contrast
        cap.set(13,0.40)      #hue
        cap.set(12,0.80)      #saturation



        mapx,mapy = self.preProcessCalib()

        if self.started != None:
            # This tells all threads that preprocessing has ceased
            self.started.set()
        i = 0
        while self.keepLooking:
            i += 1
            localDidBeliefChange = False
             # Take each frame
            _, frame = cap.read()

            # We draw on raw_frame
            raw_frame = self.preProcess(mapx,mapy,frame,0)

            # frame gets modified for colour detection
            frame = self.preProcess(mapx,mapy,frame,0)
            cv2.imshow("PROCESSED", frame)


            # Convert BGR to HSV
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            curr_ball = self.find_ball(hsv)

            # WHAT IS PHANTOM????????????

            old_ball = Ball(0,0,0,0,0, phantom=True)
            if curr_ball != None:
                old_ball = self.beliefs.ball
                self.beliefs.ball = curr_ball
                localDidBeliefChange = True
                #print 'ball moved'

            # Why does this exist?????????
            if old_ball == None:
                self.beliefs.ball = curr_ball
                localDidBeliefChange = True

            if curr_ball == None:
                curr_ball = Ball(0,0,0,0,0, phantom=True)
                self.beliefs.ball = old_ball

            last_balls = [curr_ball] + last_balls
            self.ball = copy.copy(self.beliefs.ball)

            last_balls.pop()

            # curr_ball direction/velocity not recorded in last balls
            last_balls = self.find_direction(last_balls)

            hsv_frame = hsv
            
            frame2 = self.draw_ball(curr_ball,raw_frame)

            yellow_plates = self.track_plate(hsv_frame, "yellow")
            yellow_robot_1 = yellow_plates[0]
            yellow_robot_2 = yellow_plates[1]

            blue_plates = self.track_plate(hsv_frame, "blue")
            blue_robot_1 = blue_plates[0]
            blue_robot_2 = blue_plates[1]


            if(yellow_robot_2 != None):
                yellow_robot_2_frame = hsv_frame[yellow_robot_2.y-30:yellow_robot_2.y+30, yellow_robot_2.x-30:yellow_robot_2.x+30]
                yellow_2_main_colour = self.colour_density(yellow_robot_2_frame)
                yellow_2_orientation_dot = self.track_orientation_dot(yellow_robot_2_frame, yellow_2_main_colour)
                yellow_angle_2 = self.orientation(yellow_robot_2, yellow_2_orientation_dot)
                # CHANGED EQUATION TO ACCONUT FOR EMPIRICAL ERROR ---- TO BE MODIFIED
                yellow_direc_2 = math.degrees((math.atan2(yellow_angle_2[1][1]-yellow_angle_2[0][1] , yellow_angle_2[1][0]-yellow_angle_2[0][0])))

                yellow_direc_2 = -math.degrees((math.atan2(yellow_angle_2[1][1]-yellow_angle_2[0][1] , yellow_angle_2[1][0]-yellow_angle_2[0][0])))

                yellow_robot_2.direction = yellow_direc_2

            
            if(yellow_robot_1 != None):
                yellow_robot_1_frame = hsv_frame[yellow_robot_1.y-30:yellow_robot_1.y+30, yellow_robot_1.x-30:yellow_robot_1.x+30]
                yellow_1_main_colour = self.colour_density(yellow_robot_1_frame)
                yellow_1_orientation_dot = self.track_orientation_dot(yellow_robot_1_frame, yellow_1_main_colour)
                yellow_angle_1 = self.orientation(yellow_robot_1, yellow_1_orientation_dot)
                # CHANGED EQUATION TO ACCONUT FOR EMPIRICAL ERROR ---- TO BE MODIFIED

                yellow_direc_1 = math.degrees(math.atan2(yellow_angle_1[1][1]-yellow_angle_1[0][1] , yellow_angle_1[1][0]-yellow_angle_1[0][0]))

                yellow_direc_1 = -math.degrees(math.atan2(yellow_angle_1[1][1]-yellow_angle_1[0][1] , yellow_angle_1[1][0]-yellow_angle_1[0][0]))

                yellow_robot_1.direction = yellow_direc_1
    
            if(blue_robot_1 != None):
                blue_robot_1_frame = hsv_frame[blue_robot_1.y-30:blue_robot_1.y+30, blue_robot_1.x-30:blue_robot_1.x+30]
                blue_1_main_colour = self.colour_density(blue_robot_1_frame)
                blue_1_orientation_dot = self.track_orientation_dot(blue_robot_1_frame, blue_1_main_colour)
                blue_angle_1 = self.orientation(blue_robot_1, blue_1_orientation_dot)
                # CHANGED EQUATION TO ACCONUT FOR EMPIRICAL ERROR ---- TO BE MODIFIED
                blue_direc_1 = math.degrees(math.atan2(blue_angle_1[1][1]-blue_angle_1[0][1] , blue_angle_1[1][0]-blue_angle_1[0][0]))
                blue_robot_1.direction = blue_direc_1

            if(blue_robot_2 != None):    
                blue_robot_2_frame = hsv_frame[blue_robot_1.y-30:blue_robot_1.y+30, blue_robot_1.x-30:blue_robot_1.x+30]
                blue_2_main_colour = self.colour_density(blue_robot_2_frame)
                blue_2_orientation_dot = self.track_orientation_dot(blue_robot_2_frame, blue_2_main_colour)
                blue_angle_2 = self.orientation(blue_robot_2, blue_2_orientation_dot)
                # CHANGED EQUATION TO ACCONUT FOR EMPIRICAL ERROR ---- TO BE MODIFIED

                blue_direc_2 = math.degrees(math.atan2(blue_angle_2[1][1]-blue_angle_2[0][1] , blue_angle_2[1][0]-blue_angle_2[0][0]))
                blue_direc_2 = -math.degrees(math.atan2(blue_angle_2[1][1]-blue_angle_2[0][1] , blue_angle_2[1][0]-blue_angle_2[0][0]))
                blue_robot_2.direction = blue_direc_2
    

            oldB = localDidBeliefChange
            if len(last_yellow_robot_green) > 5:
                last_yellow_robot_green.pop()

            if len(last_yellow_robot_pink) > 5:
                last_yellow_robot_pink.pop()

            if len(last_blue_robot_green) > 5:
                last_blue_robot_green.pop()

            if len(last_blue_robot_pink) > 5:
                last_blue_robot_pink.pop()

            # This set of conditionals is for determining which of the robots is determined to be
            # before now vision doesn't identify robots on colour individualy
            if yellow_1_main_colour == 'pink':
                yellow_robot_pink.roboCopy(yellow_robot_1)
                yellow_robot_green.roboCopy(yellow_robot_2)

                yellow_1_color = (255,  0,255)
                yellow_2_color = ( 37,246, 37)
            else:
                yellow_robot_green.roboCopy(yellow_robot_1)
                yellow_robot_pink.roboCopy(yellow_robot_2)

                yellow_2_color = (255,  0,255)
                yellow_1_color = ( 37,246, 37)

            if blue_1_main_colour == 'pink':
                blue_robot_pink.roboCopy(blue_robot_1)
                blue_robot_green.roboCopy(blue_robot_2)

                blue_1_color = (255,  0,255)
                blue_2_color = ( 37,246, 37)
            else:
                blue_robot_green.roboCopy(blue_robot_1)
                blue_robot_pink.roboCopy(blue_robot_2)

                blue_2_color = (255,  0,255)
                blue_1_color = ( 37,246, 37)


            #print('direction1 {}'.format(yellow_robot_pink.direction))

            #smooth out jitter in direction
            if i > 1:
                yellow_robot_pink.direction     = (yellow_robot_pink.direction + last_yellow_robot_pink[0].direction)/2
                yellow_robot_green.direction    = (yellow_robot_green.direction + last_yellow_robot_green[0].direction)/2
                blue_robot_green.direction      = (blue_robot_green.direction + last_blue_robot_green[0].direction)/2
                blue_robot_pink.direction       = (blue_robot_pink.direction + last_blue_robot_pink[0].direction)/2

                #yellow_robot_pink   = robDetection(yellow_robot_pink, last_yellow_robot_pink[0]);
                #yellow_robot_green  = robDetection(yellow_robot_green, last_yellow_robot_green[0]);
                #blue_robot_pink   = robDetection(blue_robot_pink, last_blue_robot_pink[0]);
                #blue_robot_green  = robDetection(blue_robot_green, last_blue_robot_green[0]);

                #print("last: {}".format(last_yellow_robot_pink[0].direction))
                #print("current: {}".format(yellow_robot_pink.direction))


            #Draw everything on frame
            cv2.rectangle(raw_frame, (yellow_robot_pink.x-30, yellow_robot_pink.y-30), (yellow_robot_pink.x+30, yellow_robot_pink.y+30), (  0,255,255))
            cv2.rectangle(raw_frame, (yellow_robot_green.x-30, yellow_robot_green.y-30), (yellow_robot_green.x+30, yellow_robot_green.y+30), (  0,255,255))
    
            cv2.rectangle(raw_frame, (blue_robot_pink.x-30, blue_robot_pink.y-30), (blue_robot_pink.x+30, blue_robot_pink.y+30), (255, 0, 0))
            cv2.rectangle(raw_frame, (blue_robot_green.x-30, blue_robot_green.y-30), (blue_robot_green.x+30, blue_robot_green.y+30), (255, 0, 0))

            # These lines update the persistent representations of the robots
            # with values from vision
            cpyBot = Robot(0,0,0,0,'as')

            cpyBot.roboCopy(yellow_robot_pink)
            last_yellow_robot_pink.insert(0, cpyBot)

            botChanged = robDif(yellow_robot_pink, averageBalls(last_yellow_robot_pink)) and not tooBigDif(yellow_robot_pink, cpyBot) 
            localDidBeliefChange = botChanged or localDidBeliefChange

            cpyBot = Robot(0,0,0,0,'as')
            cpyBot.roboCopy(yellow_robot_green)
            last_yellow_robot_green.insert(0, cpyBot)

            botChanged = robDif(yellow_robot_green, averageBalls(last_yellow_robot_green)) and not tooBigDif(yellow_robot_green, cpyBot) 
            localDidBeliefChange = botChanged or localDidBeliefChange

            cpyBot = Robot(0,0,0,0,'as')
            cpyBot.roboCopy(blue_robot_pink)
            last_blue_robot_pink.insert(0, cpyBot)

            botChanged = robDif(blue_robot_pink, averageBalls(last_blue_robot_pink)) and not tooBigDif(blue_robot_pink, cpyBot) 
            localDidBeliefChange = botChanged or localDidBeliefChange

            cpyBot = Robot(0,0,0,0,'as')
            cpyBot.roboCopy(blue_robot_green)
            last_blue_robot_green.insert(0, cpyBot)

            botChanged = robDif(blue_robot_green, averageBalls(last_blue_robot_green)) and not tooBigDif(blue_robot_green, cpyBot) 
            localDidBeliefChange = botChanged or localDidBeliefChange
            #print(last_yellow_robot_pink[0])
            #print(last_blue_robot_green[0])

            # Based off the above tests this deterimines if the pitch has changed
            if localDidBeliefChange:
                if self.beliefsUpdatedEvent != None:
                    self.beliefsUpdatedEvent.set()
                self.didBeliefChange = True

            cv2.line(raw_frame, yellow_angle_1[0], yellow_angle_1[1], yellow_1_color, 2)
            raw_frame = self.drawOrientation(raw_frame,yellow_robot_pink,"black")
            #cv2.circle(raw_frame, yellow_angle_1[0],3,(0,0,0),2)
            #cv2.circle(raw_frame, yellow_angle_1[1],3,(0,0,0),2)
            cv2.line(raw_frame, yellow_angle_2[0], yellow_angle_2[1], yellow_2_color, 2)
    
            cv2.line(raw_frame, blue_angle_1[0], blue_angle_1[1], blue_1_color, 2)
            cv2.line(raw_frame, blue_angle_2[0], blue_angle_2[1], blue_2_color, 2)

            cv2.imshow("final_frame", raw_frame)

            k = cv2.waitKey(1) & 0xFF

            # allow for editing of threshholds live
            if k == ord("r"):
                self.changeThresh = 1
            elif k == ord("y"):
                self.changeThresh = 2
            elif k == ord("b"):
                self.changeThresh = 3
            elif k == ord("g"):
                self.changeThresh = 4
            elif k == ord("p"):
                self.changeThresh = 5
            elif k == ord("s"):
                self.saveCalib(self.calib)
                if self.changeThresh == 1:
                    cv2.destroyWindow("red")
                elif self.changeThresh == 2:
                    cv2.destroyWindow("yellow")
                elif self.changeThresh == 3:
                    cv2.destroyWindow("blue")
                elif self.changeThresh == 4:
                    cv2.destroyWindow("green")
                elif self.changeThresh == 5:
                    cv2.destroyWindow("pink")
                self.changeThresh = 0
                self.calibActive = False

            self.calibrate(frame)

            #self.updateThresh('')

            if self.changeThresh == 1:
                lower   = self.redRange[0]
                upper   = self.redRange[1]
                mid     = self.redLower[0]
                mid2    = self.redLower[1]
                mask    = cv2.inRange(hsv, lower ,upper)
                mask2   = cv2.inRange(hsv,mid,mid2)
                mask    = mask | mask2
                mask    = self.cleanMask(mask)
                cv2.imshow("red",mask)
            elif self.changeThresh == 2:
                lower   = self.yellowRange[0]
                upper   = self.yellowRange[1]
                mask    = cv2.inRange(hsv, lower ,upper)
                mask    = self.cleanMask(mask)
                cv2.imshow("yellow",mask)
            elif self.changeThresh == 3:
                lower   = self.blueRange[0]
                upper   = self.blueRange[1]
                mask    = cv2.inRange(hsv, lower ,upper)
                mask    = self.cleanMask(mask)
                cv2.imshow("blue",mask)
            elif self.changeThresh == 4:
                lower   = self.greenRange[0]
                upper   = self.greenRange[1]
                mask    = cv2.inRange(hsv, lower ,upper)
                mask    = self.cleanMask(mask)
                cv2.imshow("green",mask)
            elif self.changeThresh == 5:
                lower   = self.pinkRange[0]
                upper   = self.pinkRange[1]
                mask    = cv2.inRange(hsv, lower ,upper)
                mask    = self.cleanMask(mask)
                cv2.imshow("pink",mask)
            time.sleep(0.05)
        cv2.destroyAllWindows()

    def terminate(self):
        ''' Function for ending the main loop by setting boolean'''
        self.keepLooking = False

    def cleanMask(self,mask):
        """
        Reduce the noise on the specified mask, by eliminating small
        groups of pixels using morphology.
        """
        kernel_dilate = np.ones((1, 1), np.uint8)
        close = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel_dilate)
        close = cv2.morphologyEx(close,cv2.MORPH_CLOSE,kernel_dilate)
        return close

    def calibrate(self,frame):
        if self.changeThresh == 1:
            cv2.namedWindow('red')
            self.createImageSliders('red')
        elif self.changeThresh == 2:
            cv2.namedWindow("yellow")
            self.createImageSliders('yellow')
        elif self.changeThresh == 3:
            cv2.namedWindow("blue")
            self.createImageSliders('blue')
        elif self.changeThresh == 4:
            cv2.namedWindow("green")
            self.createImageSliders('green')
        elif self.changeThresh == 5:
            cv2.namedWindow("pink")
            self.createImageSliders('pink')
    

    def createImageSliders(self,name):
        if name == 'red':
            cv2.createTrackbar('Hue Lower',name,self.redRange[0,0],180,self.updateThresh)
            cv2.createTrackbar('Hue Upper',name,self.redRange[1,0],180,self.updateThresh)
            cv2.createTrackbar('Sat Lower',name,self.redRange[0,1],255,self.updateThresh)
            cv2.createTrackbar('Val Lower',name,self.redRange[0,2],255,self.updateThresh)
        elif name == 'yellow':
            cv2.createTrackbar('Hue Lower',name,self.yellowRange[0,0],180,self.updateThresh)
            cv2.createTrackbar('Hue Upper',name,self.yellowRange[1,0],180,self.updateThresh)
            cv2.createTrackbar('Sat Lower',name,self.yellowRange[0,1],255,self.updateThresh)
            cv2.createTrackbar('Val Lower',name,self.yellowRange[0,2],255,self.updateThresh)
        elif name == 'blue':
            cv2.createTrackbar('Hue Lower',name,self.blueRange[0,0],180,self.updateThresh)
            cv2.createTrackbar('Hue Upper',name,self.blueRange[1,0],180,self.updateThresh)
            cv2.createTrackbar('Sat Lower',name,self.blueRange[0,1],255,self.updateThresh)
            cv2.createTrackbar('Val Lower',name,self.blueRange[0,2],255,self.updateThresh)
        elif name == 'green':
            cv2.createTrackbar('Hue Lower',name,self.greenRange[0,0],180,self.updateThresh)
            cv2.createTrackbar('Hue Upper',name,self.greenRange[1,0],180,self.updateThresh)
            cv2.createTrackbar('Sat Lower',name,self.greenRange[0,1],255,self.updateThresh)
            cv2.createTrackbar('Val Lower',name,self.greenRange[0,2],255,self.updateThresh)
        elif name == 'pink':
            cv2.createTrackbar('Hue Lower',name,self.pinkRange[0,0],180,self.updateThresh)
            cv2.createTrackbar('Hue Upper',name,self.pinkRange[1,0],180,self.updateThresh)
            cv2.createTrackbar('Sat Lower',name,self.pinkRange[0,1],255,self.updateThresh)
            cv2.createTrackbar('Val Lower',name,self.pinkRange[0,2],255,self.updateThresh)

    def saveCalib(self,con):
        #dump to yaml file
        stream = file('vision.yaml','w')
        self.calib['redRange']      = self.redRange.tolist()
        self.calib['redLower']      = self.redLower.tolist()
        self.calib['yellowRange']   = self.yellowRange.tolist()
        self.calib['blueRange']     = self.blueRange.tolist()
        self.calib['pinkRange']     = self.pinkRange .tolist()
        self.calib['greenRange']    = self.greenRange.tolist()
        yaml.dump(self.calib,stream)
        stream.close()

    def updateThresh(self,val):
        window = ''
        if self.changeThresh == 1:
            window = 'red'
        elif self.changeThresh == 2:
            window = 'yellow'
        elif self.changeThresh == 3:
            window = 'blue'
        elif self.changeThresh == 4:
            window = 'green'
        elif self.changeThresh == 5:
            window = 'pink'
        hu = cv2.getTrackbarPos('Hue Upper',window)
        hl = cv2.getTrackbarPos('Hue Lower',window)
        sl = cv2.getTrackbarPos('Sat Lower',window)
        vl = cv2.getTrackbarPos('Val Lower',window)
        if self.changeThresh == 1:
            self.redRange[0,0] = hl
            self.redRange[0,1] = sl
            self.redRange[0,2] = vl
            self.redRange[1,0] = hu
        elif self.changeThresh == 2:
            self.yellowRange[0,0] = hl
            self.yellowRange[0,1] = sl
            self.yellowRange[0,2] = vl
            self.yellowRange[1,0] = hu
        elif self.changeThresh == 3:
            self.blueRange[0,0] = hl
            self.blueRange[0,1] = sl
            self.blueRange[0,2] = vl
            self.blueRange[1,0] = hu
        elif self.changeThresh == 4:
            self.greenRange[0,0] = hl
            self.greenRange[0,1] = sl
            self.greenRange[0,2] = vl
            self.greenRange[1,0] = hu
        elif self.changeThresh == 5:
            self.pinkRange[0,0] = hl
            self.pinkRange[0,1] = sl
            self.pinkRange[0,2] = vl
            self.pinkRange[1,0] = hu

    def order_points(self,pts):
        rect = np.zeros((4,2),dtype="float32")
        s = pts.sum(axis = 1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        diff = np.diff(pts, axis = 1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        return rect

    def four_point_transform(self,image, pts):
        #obtain a consistent order of the points and unpack them individually
        rect = self.order_points(pts)
        (tl,tr,br,bl) = rect
        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        dst = np.array([
            [0,0],
            [639,0],
            [639,479],
            [0,479]], dtype = "float32")

        M = cv2.getPerspectiveTransform(rect,dst)
        warped = cv2.warpPerspective(image,M,(640,480))
        return warped

    def find_ball(self,frame):
        """
        takes in a frame
        returns an Object with the position of the ballDelta
        """

        # range for red ball
        lower_red   = self.redRange[0]
        upper_red   = self.redRange[1]
        mid         = self.redLower[0]
        mid2        = self.redLower[1]
        mask2       = cv2.inRange(frame,mid,mid2)
        
    
        # mask is the combination of red and blue masks
        red_mask    = cv2.inRange(frame,lower_red ,upper_red)
        mask        = red_mask 
        mask        = mask | mask2
        #-------------------DEBUG--------------------------
        #cv2.imshow("mask",mask)
        #--------------------------------------------------
        # dilate the image to make contours bigger, then close it to improve recognition
        kernel = np.ones((2,2), np.uint8)
        kernel2 = np.ones((5,5),np.uint8)
        frame_mask = cv2.dilate(mask, kernel)#, iterations=adjustments['erode'])
        closing = cv2.morphologyEx(frame_mask, cv2.MORPH_CLOSE, kernel2)
    
        # find all groupings of pixels found by mask
        im2, contours, hierarchy = cv2.findContours(closing, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
        # find area of all contours
        areas = [cv2.contourArea(c) for c in contours]
    
        if areas != []:
            largest_contour = contours[np.argmax(areas)]
            (x,y),radius = cv2.minEnclosingCircle(largest_contour)
            ball = Ball(x,y,radius,0,0)
            return ball
        return None
    
    def find_direction(self,objs):
        """
        Takes in a list of Objects (min len 2)
        finds the line of best fit through them
        returns the first Object in the list with the direction filled in
        """
        xs = []
        lastx = objs[0].x
        mag = 0
        ys = []
        for obj in objs:
            xs.append(obj.x)
            if lastx > obj.x:
                mag = 1+mag 
            elif lastx < obj.x:
                mag = mag -1
            ys.append(obj.y)
        if mag > 0:
            mag = 1
        elif mag < 0:
            mag = -1
        #print "mag direc " + str(mag)
        A = np.array([ xs, np.ones(len(objs))])
        mag = mag * (abs(xs[1]-xs[0]) + abs(ys[1]-ys[0]))
    
        m, c = np.linalg.lstsq(A.T,ys)[0] # obtaining the parameters
        #slope, intercept, r_value, p_value, std_err = stats.linregress(xs,ys)
        #objs[0].direction = np.arctan(w[0])
        objs[0].direction = m
        objs[0].magnitude = mag
        return objs

    def preProcessCalib(self):
        # termination criteria
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        objp = np.zeros((8*5,3), np.float32)
        objp[:,:2] = np.mgrid[0:8,0:5].T.reshape(-1,2)

        # Arrays to store object points and image points from all the images.
        objpoints = [] # 3d point in real world space
        imgpoints = [] # 2d points in image plane.
        #images = glob.glob('./Preprocessing/Pitch0/*.png')
        images = glob.glob('./Preprocessing/Pitch1/*.png')
        for fname in images:
            img = cv2.imread(fname)
            gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
            # Find the chess board corners
            ret, corners = cv2.findChessboardCorners(gray, (8,5),None)
            # If found, add object points, image points (after refining them)
            if ret == True:
                objpoints.append(objp)
                
                corners2 = cv2.cornerSubPix(gray,corners,(11,11),(-1,-1),criteria)
                imgpoints.append(corners2)

                # Draw and display the corners
                img = cv2.drawChessboardCorners(img, (8,5), corners2,ret)
                
                #cv2.imshow('img',img)
                #cv2.waitKey(500)

        #cv2.destroyAllWindows()

        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)
        #img = cv2.imread('../Eyes/calib2/snap-unknown-20160208-155754-1.jpeg')
        h,  w = 480, 640
        newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))

        # undistort
        mapx,mapy = cv2.initUndistortRectifyMap(mtx,dist,None,newcameramtx,(w,h),5)
        return mapx,mapy

    def preProcess(self,mapx,mapy,img,type):
        #refPt = [(56, 48), (52, 434), (597, 456), (601, 46)]  # Pitch
        refPt = [(51, 47), (58, 442), (579, 441), (593, 58)]
        dst = cv2.remap(img,mapx,mapy,cv2.INTER_LINEAR)
        if type == 0:
            kernel = np.ones((2,2), np.uint8)
            opened = cv2.morphologyEx(dst, cv2.MORPH_OPEN, kernel)
            dilated = cv2.dilate(opened, kernel, iterations = 1)
        else:
            dilated = dst
        fixed = self.four_point_transform(dilated,np.asarray(refPt))
        return fixed

    def draw_ball(self,obj,frame):
        """
        Takes in an Object and frame
        Draws a circle around the Object
        draws a line in the correct direction
        returns modified frame
        """
        center = (int(obj.x),int(obj.y))
        #projected = (int(obj.magnitude*10* np.cos(obj.direction)) , int(obj.magnitude *10* np.sin(obj.direction)))
        #y1 = y0 - x0*slope + x1*slope
    
        projected = (center[0]+int(obj.magnitude*10),0)
        projected = (int(projected[0]),int(center[1] - center[0]*obj.direction + projected[0]*obj.direction))
        #projected = (int(center[0]+projected[0]),int(center[1]+projected[1]))
        #print "current   " +str(center[0]) + ", " + str(center[1])
        #print "magnitude " + str(obj.magnitude+ center[0])
        #print "projected " +str(projected[0]) + ", " + str(projected[1])
        cv2.circle(frame,center,int(obj.size),(0,0,255),2)
        cv2.line(frame, center,projected,(0,0,255),2)
        return frame

    def track_plate(self, frame, colour):
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
            lower_boundary = self.yellowRange[0]
            upper_boundary = self.yellowRange[1]
    
        elif (colour == "blue"):
            lower_boundary = self.blueRange[0]
            upper_boundary = self.blueRange[1]
    
        # The mask contains the pixels which are in the colour boundary
        mask = cv2.inRange(frame, lower_boundary, upper_boundary)
        #cv2.imshow(colour,mask)
    
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
    
        robot_1 = Object(0, 0, 0, 0)
        robot_2 = Object(0, 0, 0, 0)
    
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
            robot_1 = Object(270, 270, 0, 0)
            robot_2 = Object(270, 270, 0, 0)
            return (robot_1, robot_2)


    def colour_density(self,robot_frame):
        """
        The function determines the dominating colour on the plate.
        """

        pink_mask = cv2.inRange(robot_frame,self.pinkRange[0],self.pinkRange[1])
        green_mask = cv2.inRange(robot_frame,self.greenRange[0],self.greenRange[1])
        
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
    
    
    def track_orientation_dot(self,robot_frame, colour):
        """
        Finds the single dot on the plate, based on its colour
        """
        orientation_dot = Object(0, 0, 0, 0)
    
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
        #cv2.iYshow("self.track_orientation_dot", mask)
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
    
            orientation_dot = Object(x, y, 0, 0)
            return orientation_dot
        else:
            return orientation_dot
    
    def orientation(self,team_dot, orientation_dot):
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
    
    
        # return ((team_dot.x, team_dot.y), (int(v_2[0]), int(v_2[1])))
        return ((team_dot.x, team_dot.y), new_point)

    def drawOrientation(self,raw_frame,robot,color):
        rotated_point = ( int(robot.x + 10*math.cos(math.radians(robot.direction))),int(robot.y - 10*math.sin(math.radians(robot.direction))) )
        cv2.line(raw_frame, (robot.x,robot.y), rotated_point, (0,0,0), 2)
        return raw_frame

def tooBigDif(rob1, rob2):
    if abs(rob1.x - rob2.x) > 15 or abs(rob1.y - rob2.y) > 15:
        return False
    else: return True

def robDif(rob1, rob2):
    if math.sqrt((rob1.x - rob2.x)**2 + (rob1.y - rob2.y)**2) > 5:
        return True
    else:
        return False

def robDetection(robot, last_robot):
    # takes in current robot and last robot
    # threshholds the position change of the robot

    if abs(robot.x - last_robot.x) < 4 or abs(robot.x - last_robot.x) > 50:
        if abs(robot.x - last_robot.x) <100:
            robot.x = last_robot.x
    if abs(robot.y - last_robot.y) < 4 or abs(robot.y - last_robot.y) > 50:
	if abs(robot.y - last_robot.y) <100:
	    robot.y = last_robot.y
    #if abs(robot.direction - last_robot.direction) < 3 or abs(robot.direction - last_robot.direction) > 100:
    #    robot.direction = last_robot.direction
    return robot
    

def averageBalls(balls):
    sumX = 0
    sumY = 0
    for i in balls:
        sumX += i.x
        sumY += i.y
    sumX = sumX/len(balls)
    sumY = sumY/len(balls)
    return Ball(sumX,sumY,0,0,0)
        
def main():
    import yaml
    beliefs = State()
    #beliefs = State()

    conf = yaml.load(file('setup.yaml').read())

    # Adds the goals from the config file
    defend = conf['Goals']['defend']
    beliefs.goalToDefend = Goal(defend[0], defend[1])
    attack = conf['Goals']['attack']
    beliefs.goalToScore = Goal(attack[0], attack[1], True)

    # Identify and create the robots from config file information
    teamColour = conf['Teams']['allies']
    enemyColour = conf['Teams']['enemies']

    myColour = conf['MyColour']
    allyColour = [color for color in conf['UnitColours'] if color != myColour][0]

    beliefs.teammate = Robot(0, 0, 0, 0, '{}'.format(teamColour[0]+allyColour[0]))
    beliefs.me = Robot(0, 0, 0, 0, '{}'.format(teamColour[0]+myColour[0]))


    beliefs.adv1 = Robot(0, 0, 0, 0, enemyColour[0]+allyColour[0])
    beliefs.adv2 = Robot(0, 0, 0, 0, enemyColour[0]+myColour[0])

    # Colour assignments dictonary allows us to decouple the robots colourings
    # from the code
    beliefs.colourAssignments[teamColour] = {}
    beliefs.colourAssignments[enemyColour] = {}

    beliefs.colourAssignments[teamColour][myColour] = beliefs.me
    beliefs.colourAssignments[teamColour][allyColour] = beliefs.teammate
    beliefs.colourAssignments[enemyColour][allyColour] = beliefs.adv1
    beliefs.colourAssignments[enemyColour][myColour] = beliefs.adv2


    eyes = Eye(beliefs)
    try:
        eyes.startLooking()
    except KeyboardInterrupt:
        print 'exiting'
        exit(0)

if __name__ == '__main__':
    main()
