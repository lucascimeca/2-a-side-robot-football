import cv2
import numpy as np
from scipy import stats
from dataStructures import Object

import time

cap = cv2.VideoCapture(1)

# positions of last 5 balls
last_balls = [Object(0,0,0,0,0),Object(0,0,0,0,0),Object(0,0,0,0,0),Object(0,0,0,0,0),Object(0,0,0,0,0)]
# old
ballPos2 = (0,0)
ballPos  = (0,0)


def track_ball(frame):
	"""
	takes in a frame and the position of ball highlited 
	"""
	global ballPos
	global ballPos2
	# range for red ball
	lower_red   = np.array([-5,160,100])
	upper_red   = np.array([  5,255,255])

    # mask is the combination of red and blue masks
	red_mask    = cv2.inRange(frame,lower_red ,upper_red)
	mask 		= red_mask 
	cv2.imshow("mask",mask)
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
		center = (int(x),int(y))
		ballLastAvg = ((ballPos[0]+ballPos2[0])/2,(ballPos[1]+ballPos2[1])/2)
		ballNowAvg  = ((ballPos[0]+center[0])/2,(ballPos[1]+center[1])/2)
		ballDelta   = (ballLastAvg[0]-ballNowAvg[0],ballLastAvg[1]-ballNowAvg[1])
		# ballDelta = (ballPos[0]-center[0] ,ballPos[1]- center[1])
		ballDelta = (-10*ballDelta[0],-10*ballDelta[1]) 
		ballDelta = (center[0]+ballDelta[0], center[1]+ballDelta[1])
		cv2.line(frame, center,ballDelta,(0,0,255),2)
		ballPos2 = ballPos
		ballPos  = center
		radius   = int(radius)
		cv2.circle(frame,center,radius,(0,0,255),2)
		return frame
	return frame

def find_ball(frame):
	"""
	takes in a frame
	returns an Object with the position of the ballDelta
	"""
	# range for red ball
	lower_red   = np.array([-5,160,100])
	upper_red   = np.array([  5,255,255])

    # mask is the combination of red and blue masks
	red_mask    = cv2.inRange(frame,lower_red ,upper_red)
	mask 		= red_mask 
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
		ball = Object(x,y,radius,0,0)
		return ball
	return Object(0,0,0,0,0)




def find_direction(objs):
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
	print "mag direc " + str(mag)
	A = np.array([ xs, np.ones(len(objs))])
	mag = mag * (abs(xs[1]-xs[0]) + abs(ys[1]-ys[0]))

	m, c = np.linalg.lstsq(A.T,ys)[0] # obtaining the parameters
	#slope, intercept, r_value, p_value, std_err = stats.linregress(xs,ys)
	#objs[0].direction = np.arctan(w[0])
	objs[0].direction = m
	objs[0].magnitude = mag
	return objs[0]

def draw_ball(obj,frame):
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
	print "current   " +str(center[0]) + ", " + str(center[1])
	print "magnitude " + str(obj.magnitude+ center[0])
	print "projected " +str(projected[0]) + ", " + str(projected[1])
	cv2.circle(frame,center,int(obj.size),(0,0,255),2)
	cv2.line(frame, center,projected,(0,0,255),2)
	return frame



while(1):
	 # Take each frame
	_, frame = cap.read()

	# Convert BGR to HSV
	hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

	# find the ball
	hsv = track_ball(hsv)

	curr_ball = find_ball(hsv)
	last_balls = [curr_ball] + last_balls
	last_balls.pop()
	curr_ball = find_direction(last_balls)
	
	





	cv2.imshow('tracking',hsv)
	frame2 = draw_ball(curr_ball,frame)
	cv2.imshow('newDraw',frame2)
	k = cv2.waitKey(5) & 0xFF
	if k == 27:
	    break

cv2.destroyAllWindows()