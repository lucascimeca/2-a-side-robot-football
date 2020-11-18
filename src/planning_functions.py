
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
        
    # if and when backMotion is changed to True, the plan will plan to
    # reach the point with backward motion
    backMotion = False
    plan = []
    angleToReach = angleToPoint(currentPoint, pointToReach)
    
    if(isBackMotion(currentDirection, angleToReach)):
        backMotion = True
        
    #---- implements forward motion---
    if(not(backMotion)):
        plan.append(planToTurn(currentDirection, angleToReach))
        distToPoint = int(round(dist(currentPoint, pointToReach)))
        reminder = distToPoint
        while (reminder>50):
            plan.append('f50')
            reminder-=50
        plan.append('f'+str(reminder))
            
    #---- implements backward motion----
    else:
        backDirection = sumDegrees(currentDirection, 180)
        plan.append(planToTurn(backDirection, angleToReach))
        distToPoint = int(round(dist(currentPoint, pointToReach)))
        reminder = distToPoint
        while (reminder>50):
            plan.append('b50')
            reminder-=50
        plan.append('b'+str(reminder))
        angleToReach = sumDegrees(angleToReach, 180)
    return [plan,angleToReach] 
        
# plan to reach a point, given the other robots in the field
# the resulting plan will take into account routing around objects on the way
def planToPointInGame(state, pointToGo):
    myPosition = state.getMyPos()
    currentPos = myPosition
    myDirection = state.getMyDirection()
    obstaclesPositions = [state.getTeammatePos(), state.getAdvPos()[0], state.getAdvPos()[1]]
    plan = []
    
    # plans straight, no need to rout around objects
    if(not(needRouting(state, pointToGo))):
        return planToPoint(myPosition, currentDirection, pointToGo)
    # need to plan to avoid obstacles
    else:
        # retrieve all obstacles
        obstaclesToAvoid = []
        for obs in obstaclesPositions:
            if(pointToLineDistance(myPosition, pointToGo, obs)<=40):
                obstaclesToAvoid.append([obs, dist(myPosition, obs)])
        # orders list of obstacles from closest to furthest
        obstaclesToAvoid.sort(key = lambda x: x[1])
        obstaclesToAvoid = list(map(lambda x: x[0], obstaclesToAvoid))
        for obsPos in obstaclesToAvoid:
            
            #
            #        HERE
            #       .  -  .
            #     .    -    .
            #   .    (traj) . (obj)
            #     .    -    .
            #       .  -  .
            #        HERE
            #
            distanceToLine = pointToLineDistance(myPosition, pointToGo, obsPos)
            if(distanceToLine>0):
                thetaToSecondPoint = math.degrees(math.atan(20/distanceToLine))
                thetaToFirstPoint = 2*thetaToSecondPoint
                hyp = 20/math.sin(thetaToSecondPoint)
            else:
                thetaToSecondPoint = 0
                thetaToFirstPoint = 180
                hyp = 20
            #check if the object is on the right
            if(myDirection-angleToPoint(myPosition, obsPos)>0):
                pointToStartCircumvent = getPointFromPoint(obsPos, sumDegrees(myDirection, thetaToFirstPoint), hyp)
                pointToGetTo = getPointFromPoint(obsPos, sumDegrees(myDirection, thetaToSecondPoint), hyp)
                [partialPlan, myDirection ] = planToPoint(currentPos, myDirection, pointToStartCircumvent)
                plan += partialPlan
                plan += ['l45', 'f28', 'r90', 'f28', 'l45']
                currentPos = pointToGetTo
                print(pointToGetTo)
            # otherwise it's on the left of the planned trajectory
            else:
                pointToStartCircumvent = getPointFromPoint(obsPos, sumDegrees(myDirection, -thetaToFirstPoint), hyp)
                pointToGetTo = getPointFromPoint(obsPos, sumDegrees(myDirection, -thetaToSecondPoint), hyp)
                [partialPlan, myDirection ] = planToPoint(currentPos, myDirection, pointToStartCircumvent)
                plan += partialPlan
                plan += ['r45', 'f28', 'l90', 'f28', 'r45']
                currentPos = pointToGetTo
                print(pointToGetTo)
        [partialPlan, myDirection] = planToPoint(currentPos, myDirection, pointToGo)
        plan += partialPlan
        return [plan, myDirection]
        
##############################################333
# #########3OLD WORKING PLAN TO GRAB
# def planToGrab(state):

    # # retrieve state
    # myPosition = state.getMyPos()
    # myDirection = state.getMyDirection()
    # ballPosition = state.getBallPos()
    
    # plan = []
    # #needs to be flipped with respect to the x axis!!!
    # newDirection = angleToPoint(myPosition, ballPosition)
    # #DEBUG      
    # #print("my position is: "+str(myPosition)+" my direction is: "+str(myDirection))
    # #print("angle from my position to ball position is: "+str(newDirection))
    # plan.append(planToTurn(myDirection, newDirection))
      
    # distToPoint = int(round(dist(myPosition, ballPosition)))
    # if(distToPoint>=40):
      # reminder = distToPoint
      # while (reminder>50):
          # plan.append('f50')
          # reminder-=50
      # if(reminder>40):
          # plan.append('f'+str(reminder-40))
    # plan.append('gb')
          
    # return plan
    
######################################
    
def planToGrab(state):

    # retrieve state
    myPosition = state.getMyPos()
    myDirection = state.getMyDirection()
    ballPosition = state.getBallPos()
   
    # distance from the corners not to act
    d = 15
    xLimit = 295
    yLimit = 205
   
    plan = []
    angleToBall = angleToPoint(myPosition, ballPosition)

    if(ballPosition[0]<=d):
        pointToGo = getPointFromPoint(ballPosition, 90, 40)   
        [partialPlan, myDirection] = planToPoint(myPosition, myDirection, pointToGo)
        plan += partialPlan
        directionToReach = angleToPoint(pointToGo, ballPosition)
        if (directionToReach!=myDirection):
            plan.append(planToTurn(myDirection, directionToReach))
        plan.append('gb')
    elif(ballPosition[1]<=d):
        pointToGo = getPointFromPoint(ballPosition, -90, 40)   
        [partialPlan, myDirection] = planToPoint(myPosition, myDirection, pointToGo)
        plan += partialPlan
        directionToReach = angleToPoint(pointToGo, ballPosition)
        if (directionToReach!=myDirection):
            plan.append(planToTurn(myDirection, directionToReach))
        plan.append('gb')
    elif(ballPosition[0]>=(xLimit-d)):
        pointToGo = getPointFromPoint(ballPosition, 180, 40)   
        [partialPlan, myDirection] = planToPoint(myPosition, myDirection, pointToGo)
        plan += partialPlan
        directionToReach = angleToPoint(pointToGo, ballPosition)
        if (directionToReach!=myDirection):
            plan.append(planToTurn(myDirection, directionToReach))
        plan.append('gb')
    elif(ballPosition[1]>=(yLimit-d)):
        pointToGo = getPointFromPoint(ballPosition, 90, 40)   
        [partialPlan, myDirection] = planToPoint(myPosition, myDirection, pointToGo)
        plan += partialPlan
        directionToReach = angleToPoint(pointToGo, ballPosition)
        if (directionToReach!=myDirection):
            plan.append(planToTurn(myDirection, directionToReach))
        plan.append('gb')
    else:
        pointToGo = getPointFromPoint(ballPosition, sumDegrees(angleToBall, 180), 30)   
        [partialPlan, myDirection] = planToPoint(myPosition, myDirection, pointToGo)
        plan += partialPlan
        if (angleToBall!=myDirection):
            plan.append(planToTurn(myDirection, angleToBall))
        plan.append('gb') 
    return plan
    
def planToKickOff(state):
    myPosition   = state.getMyPos()
    myDirection = state.getMyDirection()
    ballPosition = state.getBallPos()
    
    plan = ['go']
    angleToBall = angleToPoint(myPosition, ballPosition)
    pointToGo = getPointFromPoint(ballPosition, angleToBall, 20)
    [partialPlan, _ ] = planToPoint(myPosition, myDirection, pointToGo)
    plan += partialPlan
    plan += ['gc', 'go', 'k50', 'gc']
    return plan
    
def planToDefend2(state):
    myPosition   = state.getMyPos()
    myDirection = state.getMyDirection()
    adv1Pos     = state.getAdvPos()[0]
    adv2Pos     = state.getAdvPos()[1]
    adv1Direction     = state.getAdvDirection()[0]
    adv2Direction     = state.getAdvDirection()[1]
    betweenDistance = dist(adv1Pos,adv2Pos)
    pointToGo = myPosition
    if(betweenDistance>40):
        pointToGo = (int((adv1Pos[0]+adv2Pos[0])/2),int((adv1Pos[1]+adv2Pos[1])/2))
    [plan, none] = planToPoint(myPosition,myDirection,pointToGo)
    return plan
    
    
def planToDefend(state):
    # retrieve state
    myPosition = state.getMyPos()
    myDirection = state.getMyDirection()
    ballPosition = state.getBallPos()
    goalToDefend = state.getGoalToDefend()
    
    pointToGo = (0,0)
    if(goalToDefend[0]==0):
        pointToGo = getPointFromPoint(goalToDefend, 0, 30)
    else:
        pointToGo = getPointFromPoint(goalToDefend, 180, 30)
        
    [plan, myDirection] = planToPoint(myPosition, myDirection, pointToGo)
    angleToReach = angleToPoint(pointToGo, ballPosition)
    if(myDirection!=angleToReach):
        plan.append(planToTurn(myDirection, angleToReach))
    return plan
    
    
    # # finds which of the two adversaries have the ball
    # adv1Dist = math.sqrt(math.pow((adv1Pos[0]-ballPos[0]),2)+math.pow((adv1Pos[1]-ballPos[1]),2))
    # adv2Dist = math.sqrt(math.pow((adv2Pos[0]-ballPos[0]),2)+math.pow((adv2Pos[1]-ballPos[1]),2))
    # if(adv1Dist<adv2Dist):
        # advPos = adv1Pos
        # advDirection = adv1Direction
    # else:
        # advPos = adv2Pos
        # advDirection = adv2Direction
        
    # #finds the position to go to to intercept the ball
    # #NOTE: coordinates must be flipped with respect to the y axis!
    # xToGo = int(math.floor(70*math.cos(advDirection*(math.pi/180))+advPos[0]))
    # yToGo = int(math.floor(-70*math.sin(advDirection*(math.pi/180))+advPos[1]))
    
    
    # # -------------DEBUG---------
    # # print("our position is "+str(myPosition[0])+" "+str(myPosition[1]))
    # # print("the adv position is "+str(advPos[0])+" "+str(advPos[1]))
    # # print("the adv direction is "+ str(advDirection))
    # # print("we want to go to "+str(xToGo)+" "+str(yToGo))
    
    
    # #plans to go to the found point
    # [plan, currentDirection] = planToPoint(myPosition, myDirection, (xToGo,yToGo))
    
    # #turns so to face the teammate
    # directionToReach = 0
    # if(advDirection+180>180):
        # directionToReach = advDirection-180
    # else:
        # directionToReach = advDirection+180
        
    # plan.append(planToTurn(currentDirection, directionToReach))
    # plan.append('go')

    # return plan
  
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
 
def planToReceivePass(state):
    myPosition   = state.getMyPos()
    myDirection = state.getMyDirection()
    teammatePosition = state.getTeammatePos()
    
    plan = []
    angle = angleToPoint(myPosition, teammatePosition)
    plan.append(planToTurn(myDirection, angle))
    return plan


def haveWeBall(state):
    myPosition = state.getMyPos()
    ballPosition = state.getBallPos()
    distance = dist(myPosition,ballPosition)
    if (distance>20):
        return False
    else:   
        return True
    
def hasEnemyBall(state):
    [adv1Pos,adv2Pos] = state.getAdvPos()
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
    
# function which returns true if there are robots in the way of the robot 
# and a point
def needRouting(state, pointToReach):
    myPos = state.getMyPos()
    robots = [state.getTeammatePos(), state.getAdvPos()[0], state.getAdvPos()[1]]
    for robot in robots:
        if (pointToLineDistance(myPos, pointToReach, robot)<40):
            return True
    return False



