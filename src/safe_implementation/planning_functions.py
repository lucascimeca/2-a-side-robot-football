
import math
from math import atan2
from base import *

#State is the object holding the state of the world at any given point in time
# all positions are (x,y) tuples in cm
# myDirection is a integer specifying the degree of rotation of the robot with 
# respect to the x plane 
# e.g. facing right -> 0deg, facing left -> 180-180deg, facing upwards (from our goal) -> 90 deg  
# facing downwards -> -90deg    etc.

# function which plans to reach a point in the field

#NOTE: needs to be upgraded to deal with moving around robots on the way!!!
def planToPoint(currentPoint, currentDirection, pointToReach):

        plan = []
        newDirection = angleToPoint(currentPoint, pointToReach)
        plan.append(planToTurn(currentDirection, newDirection))
        
        distToPoint = int(round(dist(currentPoint, pointToReach)))
        if(distToPoint>=5):
            reminder = distToPoint
            while (reminder>50):
                plan.append('f50')
                reminder-=50
            plan.append('f'+str(reminder))
            
        return [plan,newDirection] 
        
################################################################################
########################## plan to point with square motion ####################
    # plan = []
    
    # #retrieves information from thes state of the world
    # x_length = 300
    # y_length = 200
    
    # benderPos   = currentPoint
    # benderDirection = currentDirection
    
    
    # # -----plan to bring the distance along the y axis to zero-----
    # angleToReach = 0
    # distanceToY = 0
    # doNothing = 0
    # if(pointToReach[1]>benderPos[1]):
        # angleToReach = -90
        # distanceToY = pointToReach[1]-benderPos[1]
    # elif(pointToReach[1]<benderPos[1]):
        # angleToReach = 90
        # distanceToY = benderPos[1]-pointToReach[1]
    # else:
        # doNothing = 1

    # #updates plan to turn    
    # if(doNothing==0):
        # plan.append(planToTurn(benderDirection,angleToReach))
    # benderDirection = angleToReach
    
    # #updates plan to move
    # if(doNothing==0):
        # distTimes = int(math.floor(distanceToY/500))
        # remainder = int(math.floor(distanceToY%500))
        # for i in range(distTimes):
            # plan.append('f50')
        # plan.append('f'+str(remainder))

    # # -----plan to bring the distance along the x axis to zero -----     
    # distTimes = 0
    # distanceToX = 0
    # doNothing = 0
    # if(pointToReach[0]>benderPos[0]):
        # angleToReach = 0
        # distanceToX = pointToReach[0]-benderPos[0]
    # elif(pointToReach[0]<benderPos[0]):
        # angleToReach = 180
        # distanceToX = benderPos[0]-pointToReach[0]
    # else:
        # doNothing = 1
        
    # #updates plan to turn
    # if(doNothing==0):
        # plan.append(planToTurn(benderDirection,angleToReach))
    # benderDirection = angleToReach
    
    # #updates plan to move    
    # if(doNothing==0):
        # distTimes = int(math.floor(distanceToX/500))
        # remainder = int(math.floor(distanceToX%500))
        # for i in range(distTimes):
            # plan.append('f50')
        # plan.append('f'+str(remainder))

    # return [plan, benderDirection]
#######################################################################
    

def planToGrab(state):

    # retrieve state
    myPosition = state.getMyPos()
    myDirection = state.getMyDirection()
    ballPosition = state.getBallPos()
    
    plan = []
    #needs to be flipped with respect to the x axis!!!
    newDirection = angleToPoint(myPosition, ballPosition)
    #DEBUG      
    #print("my position is: "+str(myPosition)+" my direction is: "+str(myDirection))
    #print("angle from my position to ball position is: "+str(newDirection))
    plan.append(planToTurn(myDirection, newDirection))
        
    distToPoint = int(round(dist(myPosition, ballPosition)))
    if(distToPoint>=30):
        reminder = distToPoint
        while (reminder>50):
            plan.append('f50')
            reminder-=50
        if(reminder>30):
            plan.append('f'+str(reminder-30))
        if(reminder>20):
            plan.append('f'+str(reminder-20))
    plan.append('gb')
            
    return plan
    
def planToDefend(state):
    # retrieve state
    myPosition   = state.getMyPos()
    myDirection = state.getMyDirection()
    adv1Pos     = state.getAdvPos()[0]
    adv2Pos     = state.getAdvPos()[1]
    adv1Direction     = state.getAdvDirection()[0]
    adv2Direction     = state.getAdvDirection()[1]
    ballPos     = state.getBallPos()
    
    
    # finds which of the two adversaries have the ball
    adv1Dist = math.sqrt(math.pow((adv1Pos[0]-ballPos[0]),2)+math.pow((adv1Pos[1]-ballPos[1]),2))
    adv2Dist = math.sqrt(math.pow((adv2Pos[0]-ballPos[0]),2)+math.pow((adv2Pos[1]-ballPos[1]),2))
    if(adv1Dist<adv2Dist):
        advPos = adv1Pos
        advDirection = adv1Direction
    else:
        advPos = adv2Pos
        advDirection = adv2Direction
        
    #finds the position to go to to intercept the ball
    #NOTE: coordinates must be flipped with respect to the y axis!
    xToGo = int(math.floor(70*math.cos(advDirection*(math.pi/180))+advPos[0]))
    yToGo = int(math.floor(-70*math.sin(advDirection*(math.pi/180))+advPos[1]))
    
    
    # -------------DEBUG---------
    # print("our position is "+str(myPosition[0])+" "+str(myPosition[1]))
    # print("the adv position is "+str(advPos[0])+" "+str(advPos[1]))
    # print("the adv direction is "+ str(advDirection))
    # print("we want to go to "+str(xToGo)+" "+str(yToGo))
    
    
    #plans to go to the found point
    [plan, currentDirection] = planToPoint(myPosition, myDirection, (xToGo,yToGo))
    
    #turns so to face the teammate
    directionToReach = 0
    if(advDirection+180>180):
        directionToReach = advDirection-180
    else:
        directionToReach = advDirection+180
        
    plan.append(planToTurn(currentDirection, directionToReach))
    plan.append('go')

    return plan
  
# function which plans so to be able to pass the ball to a teammate
# the function assumes the ball is grabbed

#NOTE: needs to be upgraded to deal with opponents in the way!!!
def planToPass(state):

    # distance from the teammate it will reach 
    distanceFromTeammate = 40    
    
    # retrieve state    
    myPosition   = state.getMyPos()
    myDirection = state.getMyDirection()
    teammatePos = state.getTeammatePos()
    teammateDirection = state.getTeammateDirection()
    
    #computes position to go to for passing
    #NOTE: coordinates must be flipped with respect to the y axis!
    xToGo = int(math.floor(distanceFromTeammate*math.cos(teammateDirection*(math.pi/180))+teammatePos[0]))
    yToGo = int(math.floor(-distanceFromTeammate*math.sin(teammateDirection*(math.pi/180))+teammatePos[1]))
    
    
    # -------------DEBUG-------------------------------
    # print("our position is "+str(myPosition[0])+" "+str(myPosition[1]))
    # print("the teammate position is "+str(teammatePos[0])+" "+str(teammatePos[1]))
    # print("the teammate direction is "+ str(teammateDirection))
    # print("we want to go to "+str(xToGo)+" "+str(yToGo))
    # -------------------------------------------------
    
    #plans to go to the found point
    [plan, currentDirection] = planToPoint(myPosition, myDirection, (xToGo,yToGo))
    
    #turns so to face the teammate
    directionToReach = 0
    if(teammateDirection+180>180):
        directionToReach = teammateDirection-180
    else:
        directionToReach = teammateDirection+180
    
    plan.append(planToTurn(currentDirection, directionToReach))
    plan.append('go')
    plan.append('k80')
    plan.append('gc')
    
    return plan
    
def planToKick(state):

    # retrieve state
    myPosition = state.getMyPos()
    myDirection = state.getMyDirection()
    goalPosition = state.getGoalToScore()
           
    plan = []
    newDirection = angleToPoint(myPosition, goalPosition)
    plan.append(planToTurn(myDirection, newDirection))
        
    #ADD if you want to move towards the goal before kicking
    #distToPoint = int(round(dist(myPosition, goalPosition)))
    #if(distToPoint>=150):
    #    plan.append('f'+str(distToPoint-150))

    plan.append('go')
    plan.append('k150')
    plan.append('gc')
    return plan
    

# function which returns a single command to turn to a direction specified
# CHANGE IT TO -- planToTurn
def planToTurn(direction, angleToReach):
    plan = ''
    angle = direction-angleToReach
    if(angle<0):
        if(angle>=-180):
            plan = 'l'+str(abs(int(angle)))
        else:
            angle = angle + 360
            plan = 'r'+str(int(angle))
    else:
        if(angle<=180):
            plan = 'r'+str(int(angle))
        else:
            angle = 360 - angle
            plan = 'l'+str(abs(int(angle)))
            
    return plan
 
    


def angleToPoint(p1,p2):
    ''' function which returns the angle between two points relative to the
            x axis'''
    xdif = p2[0] - p1[0]
    ydif = p2[1] - p1[1]
    theta = atan2(ydif,xdif)
    theta = -math.degrees(theta)
    return theta

def dist(p1,p2):
    xT = (p1[0] - p2[0])**2
    yT = (p1[1] - p2[1])**2
    return math.sqrt(xT + yT)

# ??
def pointDFromP(p, line, d, between):
    db = dist(d, between)
    newPoint = Point()
    newPoint.setXPixel(d/db(p.getXCm() - (between.getXCm() - p.getXCm())))
    newPoint.setYPixel(d/db(p.getYCm() - (between.getYCm() - p.getYCm())))
    return newPoint


def slope(p1, p2):
    return (double(p2.getYCm()) - double(p1.getYCm()))/(double(p2.getXCm()) - double(p1.getXCm()))

def haveWeBall(state):
    myPosition = state.getMyPos()
    ballPosition = state.getBallPos()
    distance = dist(myPosition,ballPosition)
    if (distance>20):
        return False
    else:   
        return True
    
def hasEnemyBall(state):
    [adv1Pos,av2Pos] = state.getAdvPos()
    ballPosition = state.getBallPos()
    dist1 = dist(adv1Pos,ballPosition)
    dist2 = dist(adv2Pos,ballPosition)
    if(dist1<20 or dist2<20):
        return True
    else:
        return False
    
def hasTeammateBall(state):
    teammatePosition = state.getTeammatePos()
    ballPosition = state.getBallPos()
    distance = dist(teammatePosition,ballPosition)
    if (distance>20):
        return False
    else:
        return True
    return true
    
    
#-------------------- TEST ----------------------------------
## #State has to be initialized as below
## #(me=Robot(x,y,direction,magnitude),teammate=Robot(x,y,direction,magnitude),adv1=Robot(x,y,direction,magnitude),adv2=Robot#(x,y,direction,magnitude),ball=Ball(x,y,size,direction,magnitude), goalToScore=Goal(x,y,True),goalToDefend=Goal(x,y))
##---------------------
#bender = Robot(0,0,67.166,0)
#bender.setXPixel(211)
#bender.setYPixel(47)
##---------------------
#teammate = Robot(0,0,-0,0)
#teammate.setXPixel(75)
#teammate.setYPixel(50)
##---------------------
#adv1 = Robot(0,0,-90,0)
#adv1.setXPixel(225)
#adv1.setYPixel(50)
##---------------------
#adv2 = Robot(0,0,0,0)
#adv2.setXPixel(300)
#adv2.setYPixel(100)
##---------------------
#ball = Ball(0,0,20,90,0)
#ball.setXPixel(81)
#ball.setYPixel(161)
##---------------------
#goalToScore = Goal(0,0,True)
#goalToScore.setXPixel(300)
#goalToScore.setYPixel(100)
##---------------------
#goalToDefend = Goal(0,0)
#goalToDefend.setXPixel(0)
#goalToDefend.setYPixel(100)
##---------------------
#state = State(bender,teammate,adv1,adv2,ball,goalToScore,goalToDefend)
##plans to grab the ball from current position
#plan = planToGrab(state)
#print(plan)
##plans to defend the goal
#plan = planToDefend(state)
#print(plan)
##plans to kick ball into goal
#plan = planToKick(state)
#print(plan)
##plans to pass the ball to teammate
#plan = planToPass(state)
#print(plan)
