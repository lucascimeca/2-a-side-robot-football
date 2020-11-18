from base import *
import copy
from math import sqrt, atan2
import math
import time

class Planner:
    plan = []
    beliefs = []
    grabbedBall = None

    def __init__(self, beliefChangeEvent, planningCompleteEvent):
        self.beliefsUpdatedEvent = beliefChangeEvent
        self.planningCompleteEvent = planningCompleteEvent
        self.stillPlanning = True

    def updateBeliefs(self, beliefs):
        self.beliefs = copy.copy(beliefs)

    def startPlanning(self):
        plan = []
        while self.stillPlanning:
            self.plan = plan

            # This section is present in order to prevent race conditions
            # Threads waiting for a plan should use this event
            self.planningCompleteEvent.set()

            self.beliefsUpdatedEvent.wait()
            self.beliefsUpdatedEvent.clear()

            # This event indicates a plan is being formulated
            # it will be set when the plan is up to date
            self.planningCompleteEvent.clear()
            
            plan = []
            ball = self.beliefs.ball
            me = self.beliefs.me

            goalToScore = self.beliefs.goalToScore

            if ball == None or me == None or goalToScore == None:
                continue

            if not self.grabbedBall:
                distToB = dist(me, ball)
                distToB = round(distToB) - 3
    
                turnAng = angleToTurn(me,ball)
                turnAng = int(round(turnAng, 0))
    
                if turnAng > 0:
                    plan.append(TurnRight(turnAng))
                elif turnAng < 0:
                    plan.append(TurnLeft(turnAng))
    
                t = int(distToB)/10
                r = distToB % 10
                cr = [10]*t
                cr.append(int(r))
                for i in cr:
                    plan.append(Forward(i))
    
                plan.append(CloseGrab())

            else:
                # Ball is now grabbed turn and face goalToScore and fire
                distToG = round(dist(me,goalToScore))
    
                turnAng = int(round(angleToTurn(me,goalToScore)))
    
                plan.append(OpenGrab())
                if turnAng > 0:
                    plan.append(TurnRight(turnAng))
                elif turnAng < 0:
                    plan.append(TurnLeft(turnAng))
    
                plan.append(Kick(150))

    def getPlan(self):
        return self.plan

    def terminate(self):
        self.stillPlanning = False

        
    def planToPoint(self, pointToReach,  plan=[], fromPoint=None):
        plan = []
        
        if fromPoint != None:
            benderPos = fromPoint
        else:
            benderPos   = self.beliefs.getMyPos()
           
        #retrieves information from thes state of the world
        x_length = 200
        y_length = 300
    
        benderDirection = self.beliefs.getMyDirection()
    
    
        ###############################################################
        #creates internal matrix model of the field
        #all positions will have a '-' unless they are:
        #occupied by an obstacle, in which case they will
        #be 'obs'
        #if a cell is occupied by bender the position will
        #contain an integer equal to its direction (in deg) from the
        # x axis
    

        # field = [['-']*200]*300
    
        # field = mod_field(field, teammatePos, x_length, y_length, 15)
        # field = mod_field(field, adv1Pos,x_length, y_length, 15)
        # field = mod_field(field, adv2Pos,x_length, y_length, 15)
        
        # field[benderPos[0]] = field[benderPos[0]][0:benderPos[1]]+[benderDirection]+field[benderPos[0]][benderPos[1]+1:]
    
        ####################################################################
    
        # -----plan to bring the distance along the y axis to zero-----
        angleToReach = 0
        distanceToY = 0
        doNothing = 0
        if(pointToReach[1]>benderPos[1]):
            angleToReach = 270
            distanceToY = pointToReach[1]-benderPos[1]
        elif(pointToReach[1]<benderPos[1]):
            angleToReach = 90
            distanceToY = benderPos[1]-pointToReach[1]
        else:
            doNothing = 1

        #updates plan to turn    
        if(doNothing==0):
            plan.append(self.turnToAngle(benderDirection,angleToReach))
        benderDirection = angleToReach
    
        #updates plan to move
        if(doNothing==0):
            distTimes = int(math.floor(distanceToY/500))
            remainder = int(math.floor(distanceToY%500))
            for i in range(distTimes):
                plan.append('f500')
            plan.append('f'+str(remainder))

        # -----plan to bring the distance along the x axis to zero -----     
        distanceToX = 0
        doNothing = 0
        if(pointToReach[0]>benderPos[0]):
            angleToReach = 0
            distanceToX = pointToReach[0]-benderPos[0]
        elif(pointToReach[0]<benderPos[0]):
            angleToReach = 180
            distanceToX = benderPos[0]-pointToReach[0]
        else:
            doNothing = 1
        
        #updates plan to turn
        if(doNothing==0):
            plan.append(self.turnToAngle(benderDirection,angleToReach))
        benderDirection = angleToReach
    
        #updates plan to move    
        if(doNothing==0):
            distTimes = int(math.floor(distanceToX/500))
            remainder = int(math.floor(distanceToX%500))
            for i in range(distTimes):
                plan.append('f500')
            plan.append('f'+str(remainder))

        return [plan, benderDirection]
        
        
    # Point as a point object from base
    def planToPoint2(self, pointToReach,  plan=[], fromPoint=None):
        if fromPoint == None:
            fromPoint = self.beliefs.me
        ''' Plans around obstacles to reach location''' 
        # Creates the command the order to turn to face the object
        #obstacle = self.pathClear(self.beliefs.me, pointToReach)
        #if obstacle == None:
        # If our route is clear
        newDirection = angleToTurn(self.beliefs.me, pointToReach)
        print newDirection
        myDirection = self.beliefs.me.direction
        if myDirection<0:
            myDirection+=360
        plan.append(Turn(myDirection, newDirection))
        
        distToPoint = int(round(dist(self.beliefs.me, pointToReach)))
    
        plan.append(Forward(distToPoint))

#        else:
#            # Here we choose a point that clear from obstacles and route to that
#            # want to find a point that is at least the obstacles radius plus our 
#            # radius away from it but want to prevent gaming by two equidistant 
#            # object maybe with minor randomisation
#                        
#            angle = angleToPoint(self.beliefs.me, obstacle) 
#            slope = slope(self.beliefs.me, pointToReach)
#            lineToDest = Line(slope, self.beliefs.me.x, self.beliefs.me.y)
#            
#            lineThroughObstacle = lineToDest.perpLineThroughPoint(obstacle)
#
#            intersectionPoint = lineToDest.intersectionPoint(lineThroughObstacle)
#
#            newPointToReach = pointDFromP(obstacle, lineThroughObstacle, obstacle.size+self.beliefs.me.size+5, intersectionPoint)
#
#            # Plan to reach the new point then replan to get to next point
#            [plan, newDirection] = self.planToPoint(self, newPointToReach, plan)
#            [plan, newDirection] = self.planToPoint(self, pointToReach, plan, fromPoint=newPointToReach)

        return [plan, newDirection]

    def pathClear(self, point1, point2):
        for obj in self.beliefs:
            if self.between(point1, point2, obj) and not (obj.name == point1.name or obj.name == point2.name):
                return obj
        return None

    def between(self, point1, point2, isBetween):
        ''' determines if circle is between two points '''
        q = isBetween.x
        p = isBetween.y

    def planToGrab(self, plan=[]):
        distanceToBall = math.sqrt(math.pow((self.beliefs.getMyPos()[0]-self.beliefs.getBallPos()[0]),2)+math.pow((self.beliefs.getMyPos()[1]-self.beliefs.getBallPos()[1]),2))
        if(distanceToBall<=5):
            plan = []
        else:
            #computes point to go to to then grab ball
            directionToFace = angleToPoint(self.beliefs.getMyPos(),self.beliefs.getBallPos())+180
            if(directionToFace>360):
                directionToFace -= 360
        
            xToGo = int(math.floor(35*math.cos(directionToFace*(math.pi/180))+self.beliefs.getBallPos()[0]))
            yToGo = int(math.floor(-35*math.sin(directionToFace*(math.pi/180))+self.beliefs.getBallPos()[1]))
            
            [plan, newDirection ] = self.planToPoint((xToGo, yToGo), plan)
            directionToFace = angleToPoint((xToGo,yToGo),self.beliefs.getBallPos())
            plan.append(self.turnToAngle(newDirection,directionToFace))
            plan.append('gb')
        return plan
        
    def planToDefend(self, plan=[]):
        benderPos   = self.beliefs.getMyPos()
        benderDirection = self.beliefs.getMyDirection()
        adv1Pos     = self.beliefs.getAdvPos()[0]
        adv2Pos     = self.beliefs.getAdvPos()[1]
        adv1Direction     = self.beliefs.getAdvDirection()[0]
        adv2Direction     = self.beliefs.getAdvDirection()[1]
        ballPos     = self.beliefs.getBallPos()
        # goalToScorePos = self.beliefs.getGoalToScore()
        # goalToDefendPos = self.beliefs.getGoalToDefend()
        
        
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
        
        #plans to go to the found point
        [plan, currentDirection] = self.planToPoint((xToGo,yToGo), plan)
        
        #turns so to face the opponent with the ball and opens grabber
        directionToReach = 0
        if(advDirection+180>360):
            directionToReach = advDirection-180
        else:
            directionToReach = advDirection+180
            
        plan.append(self.turnToAngle(currentDirection, directionToReach))
        plan.append('go')
        return plan
        
        
    def planToDefendInGoal(self):
        benderPos   = self.beliefs.getMyPos()
        benderDirection = self.beliefs.getMyDirection()
        adv1Pos     = self.beliefs.getAdvPos()[0]
        adv2Pos     = self.beliefs.getAdvPos()[1]
        adv1Direction     = self.beliefs.getAdvDirection()[0]
        adv2Direction     = self.beliefs.getAdvDirection()[1]
        ballPos     = self.beliefs.getBallPos()
        # goalToScorePos = self.beliefs.getGoalToScore()
        # goalToDefendPos = self.beliefs.getGoalToDefend()
        
        
        # finds which of the two adversaries have the ball
        adv1Dist = math.sqrt(math.pow((adv1Pos[0]-ballPos[0]),2)+math.pow((adv1Pos[1]-ballPos[1]),2))
        adv2Dist = math.sqrt(math.pow((adv2Pos[0]-ballPos[0]),2)+math.pow((adv2Pos[1]-ballPos[1]),2))
        if(adv1Dist<adv2Dist):
            advPos = adv1Pos
            advDirection = adv1Direction
        else:
            advPos = adv2Pos
            advDirection = adv2Direction
            

    def planToReceivePass(self, plan = []):
        ''' function which initiates a recieve from teammate'''
        turnAng = angleToTurn(self.beliefs.me, self.beliefs.teammate)
        myDirection = self.beliefs.me.direction
        if myDirection<0:
            myDirection+=360
        plan.append(self.turnToAngle(myDirection, turnAng))
        plan.append('go')
        return plan

      
    def planToPass(self, plan=[]):
        ''' function which plans so to be able to pass the ball to a teammate 
              the function assumes the ball is grabbed ''' 
        x_length = 200
        y_length = 300
        
        benderPos   = self.beliefs.getMyPos()
        benderDirection = self.beliefs.getMyDirection()
        teammatePos = self.beliefs.getTeammatePos()
        teammateDirection = self.beliefs.getTeammateDirection()

        #computes position to go to for passing
        #NOTE: coordinates must be flipped with respect to the y axis!
        xToGo = int(math.floor(35*math.cos(teammateDirection*(math.pi/180))+teammatePos[0]))
        yToGo = int(math.floor(-35*math.sin(teammateDirection*(math.pi/180))+teammatePos[1]))
        
        #plans to go to the found point
        [plan, currentDirection] = self.planToPoint((xToGo,yToGo), plan)
        
        #turns so to face the teammate
        directionToReach = 0
        if(teammateDirection+180>360):
            directionToReach = teammateDirection-180
        else:
            directionToReach = teammateDirection+180

        #pass the ball
        plan.append(self.turnToAngle(currentDirection, directionToReach))
        plan.append('go')
        plan.append('k50')
        plan.append('gc')
       
        return plan
        
    def planToKick(self, plan=[]):
        x_length = 200
        y_length = 300
        
        benderPos   = self.beliefs.getMyPos()
        benderDirection = self.beliefs.getMyDirection()
        goalPos = self.beliefs.getGoalToScore()
        
        #computes position to go to for passing
        #NOTE: coordinates must be flipped with respect to the y axis!
        xToGo = int(math.floor(90*math.cos(270*(math.pi/180))+goalPos[0]))
        yToGo = int(math.floor(-90*math.sin(270*(math.pi/180))+goalPos[1]))
        
        #plans to go to the found point
        [plan, currentDirection] = planToPoint((xToGo,yToGo), plan)
        
        
        #turns so to face the goal to score
        
        #to compute angle directly do (for after milestone 3 perhaps)
        #arctan(deltaY / deltaX) * 180 / PI
        
        directionToReach = 90
        plan.append(self.turnToAngle(currentDirection, directionToReach))
        
        plan.append(self.turnToAngle(currentDirection, directionToReach))
        plan.append('go')
        plan.append('k150')
        plan.append('gc')
        
        return plan
        
    
    def mod_field(self, field, myPos, x_length, y_length, dim):
        ''' function which modifies the field representation 
              by considering the dimensions of the robots ''' 
        halfDim = int(math.floor(dim/2))+1
        x = myPos[0]
        y = myPos[1]
        xfrom   = 0
        xto     = x_length
        yfrom   = 0
        yto     = y_length
        if (x-halfDim>=0):
            xfrom = x-halfDim
        if (y-halfDim>0):
            yfrom = y-halfDim
        if ((x+halfDim)<x_length):
            xto = x+halfDim
        if ((y+halfDim)<y_length):
            yto = y+halfDim
            
        for i in range(len(field)):
            if(i>=xfrom and i<=xto):
                field[i] = field[i][0:yfrom]+[['obs']*dim]+field[i][yto+1:]
        return field
    
    
    def turnToAngle(self, direction, angleToReach):
        ''' function which returns a single command to turn to a direction specified '''
        turnCmd = None
        if(direction<angleToReach):
            if((angleToReach-direction)<=180):
                angle = angleToReach-direction
                turnCmd = 'l'+str(angle)
            else:
                angle = 360 - angleToReach-direction
                turnCmd = 'r'+str(angle)
        elif(direction>=angleToReach):
            if((direction-angleToReach)<=180):
                angle = direction-angleToReach
                turnCmd = 'r'+str(angle)
            else:
                angle = 360 - direction-angleToReach
                turnCmd = 'l'+str(angle)
                
        return turnCmd
