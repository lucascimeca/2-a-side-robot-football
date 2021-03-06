# New set of action functions that can be modified in this file instead of 
# needing to hardcode the arduino commands
from math import atan2
import math


# Modified to take account of the more object-centric approach but maintaining the same API
# this class maintains the state representation of the pitch
# NOTE: make the state more robust by allowing for the absence of objects on pitch
class State:
    ''' State class contains the representations for all critical field objects '''
    def __init__(self, me=None,teammate=None,adv1=None,adv2=None,ball=None, goalToScore=None,goalToDefend=None):
        self.me = me
        self.teammate = teammate
        self.adv1 = adv1
        self.adv2 = adv2
        self.ball = ball
        self.goalToScore = goalToScore
        self.goalToDefend = goalToDefend
        self.colourAssignments = {}

        self.iterator = 0

    def copy(self):
        me = self.me.copy()
        teammate = self.teammate.copy()
        adv1 = self.adv1.copy()
        adv2 = self.adv2.copy()
        ball = self.ball.copy()
        goalToScore = self.goalToScore.copy()
        goalToDefend = self.goalToDefend.copy()

        return State(me,teammate,adv1,adv2,ball, goalToScore,goalToDefend)

    def setTeammate(self, teammate):
        self.teammate = teammate
#-------------------------------------------
    # returns position of our robot
    def getMyPos(self):
        return (self.me.getXCm(),self.me.getYCm())
         
    # returns bender's direction
    def getMyDirection(self):
        return self.me.direction
   
    def getMySpeed(self):
        return self.ball.magnitude
#-------------------------------------------  
    # returns position of our reammate
    def getTeammatePos(self):
        return (self.teammate.getXCm(),self.teammate.getYCm())

    def getTeammateDirection(self):
        return self.teammate.direction

    def getTeammateSpeed(self):
        return self.ball.magnitude
#--------------------------------------------
    # returns a list Object instaces. The objects retain the
    # positions of the adversaries in the field
    def getAdvPos(self):
        return [(self.adv1.getXCm(),self.adv1.getYCm()), (self.adv2.getXCm(),self.adv2.getYCm())]
      
    def getAdvDirection(self):
        return [self.adv1.direction, self.adv2.direction]
        
    def getAdvSpeed(self):
        return [self.adv1.magnitude,self.adv2.magnitude]
#--------------------------------------------
    # returns the position of the ball
    def getBallPos(self):
        return (self.ball.getXCm(), self.ball.getYCm())

    def getBallDirection(self):
        return self.ball.direction
        
    def getBallSpeed(self):
        return self.ball.magnitude
#---------------------------------------------      
    # returns enemy goal position
    def getGoalToScore(self):
        return (self.goalToScore.getXCm(), self.goalToScore.getYCm())
        
    # returns our goal position
    def getGoalToDefend(self):
        return (self.goalToDefend.getXCm(), self.goalToDefend.getYCm())

    # code for making state an iterable object
    def __iter__(self):
        return self

    def next(self):
        if self.iterator < 7:
            self.iterator += 1
            return self[self.iterator]
        else:
            raise StopIteration()

    def __getitem__(self,i):
        if i == 0:
            return self.ball
        if i == 1:
            return self.me
        if i == 2:
            return self.teammate
        if i == 3:
            return self.adv1
        if i == 4:
            return self.adv2
        if i == 5:
            return self.goalToScore
        if i == 6:
            return self.goalToDefend

    def __setitem__(self,i, to):
        if i == 0:
            self.ball = to
        if i == 1:
            self.me = to
        if i == 2:
            self.teammate = to
        if i == 3:
            self.adv1 = to
        if i == 4:
            self.adv2 = to
        if i == 5:
            self.goalToScore = to
        if i == 6:
            self.goalToDefend = to


# Object parent class of all objects on field hence should contain all information needed
# by planning systems
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def copy(self):
        return Point(self.x, self.y)

    def __getitem__(self, i):
        if i == 0:
            return self.x 
        elif i == 1:
            return self.y

    def myPos(self):
        return (self.x, self.y)

    def setXPixel(self, cm):
        self.x = int(round(cm/(297.0/640.0)))
    
    def setYPixel(self, cm):
        self.y = int(round(cm/(214.0/480.0)))
        
    def getXCm(self):
        return int(round(self.x *(297.0/640.0)))

    def getYCm(self):
        return int(round(self.y * (214.0/480.0)))
    
    def __str__(self):
        return '({}, {})'.format(self.x, self.y)


    def __getitem__(self,i):
        if i == 0:
            return self.x
        if i == 1:
            return self.y

    def __setitem__(self,i, to):
        if i == 0:
            self.x = to
        if i == 1:
            self.y = to

class Line(Point):
    def __init__(self, slope, x, y):
        self.slope = slope
        self.x = x
        self.y = y

    def onLine(self, point):
        return (point.getYCm() - self.getYCm()) - self.slope*(point.getXCm() - self.getXCm()) == 0

    def perpLineThroughPoint(self, point):
        newSlope = -(1.0/self.slope)
        return Line(newSlope, point.x, point.y)

    def intersectionPoint(self, line):
        newX = ((self.y - line.y) + (self.slope*self.x + line.slope*line.x))/(self.slope - line.slope)
        newY = self.slope(newX - self.x) + self.y

        return Point(newX, newY)

class Object(Point):
    def __init__(self,x,y,direction,magnitude, name='unnamed'):
        self.x = x
        self.y = y
        self.name = name 
        self.direction  = direction
        # sum of x and y components since last frame
        self.magnitude  = magnitude

    def copy(self):
        x = self.x
        y = self.y
        name = self.name
        magnitude = self.magnitude

        return Object(self,x,y,direction,magnitude, 'unnamed')

class Goal(Object):
    def __init__(self,x,y, attack=False, name='unnamed'):
        self.x = x
        self.y = y
        self.attack = attack

    def copy(self):
        x = self.x
        y = self.y
        attack = self.attack

        return Goal(x,y,attack, 'unnamed')

class Ball(Object):
    def __init__(self,x,y,size,direction,magnitude, holder=None, name='ball', phantom=False):
        self.x = x
        self.y = y
        self.name = name 
        self.size = size
        self.direction  = direction
        # sum of x and y components since last frame
        self.magnitude  = magnitude
        self.phantom = phantom
        # This line allows us to identify if the ball is being held and by whom

    def copy(self):
        x = self.x
        y = self.y
        name = self.name[:]
        size = self.size
        direction  = self.direction
        magnitude  = self.magnitude
        return Ball(x,y,size,direction,magnitude,'ball')

class Robot(Object):
    def __init__(self, x, y, direction, magnitude, name='unnamed'):
        self.direction = direction
        self.x = x
        self.y = y
        self.name = name
        self.magnitude = magnitude

    def copy(self):
        self.x = x
        self.y = y
        self.direction  = direction
        self.magnitude  = magnitude

        return Robot(x,y,direction,magnitude,self.name[:])

    def roboCopy(self, robot):
        self.x = robot.x
        self.y = robot.y
        self.direction  = robot.direction
        # sum of x and y components since last frame
        self.magnitude  = robot.magnitude
        return (abs(self.x - robot.x) > 3) or (abs(self.y - robot.y) > 3)
       
# class holding the information of a circle       
class MyCircle(Object):
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
       
    def getCenter():
        return self.center
     
    def getRadius():
        return self.radius
        
# class holding the information of a line     
class MyLine(Object):
    def __init__(self, point1, point2):
        self.p1 = point1
        self.p2 = point2
       
    def getP1():
        return self.p1
        
    def getP2():
        return self.p2
       
    def getSlope():
        return ((self.p1[1]-self.p2[1])/(self.p1[0]-self.p2[0]))
        
    def getConstant():
        return (self.p2[1]-(self.getSlope()*self.p2[0]))
     
# method that given a circle and a line returns true if the line intercepts the circle 
# in two points     
def lineInterceptsCircle(circle, line):
    D = line.getP1()[0]*line.getP2()[1]-line.getP2()[0]*line.getP1[1]
    d = dist(line.getP1(), line.getP2())
    r
       
    
def reachedDirection(currentDirection, directionToReach):
    if(abs(currentDirection-directionToReach)>8):
        return False
    else:
        return True
        
# functions which sums two degree values and returns one that's within -180 and +180
def sumDegrees(deg1, deg2):
    sum =  deg1+deg2
    if(sum>=180):
        return sum-360
    elif(sum<=-180):
        return sum+360
    else:
        return sum
    
#this function takes in input the current direction of the robot and the direction to reach and 
#returns True, if turning and moving backwards is more efficient than forward motion
def isBackMotion(currentDirection, directionToGo):
    backDirection = sumDegrees(currentDirection,180)
    if (abs(currentDirection-directionToGo)>90):
        return True
    return False

# given three points, this function returns the distance between the third point and the line
# traced between the first and second point
def pointToLineDistance(point1, point2, point3):
    return (abs(((point2[0]-point1[0])*(point1[1]-point3[1]))-((point1[0]-point3[0])*(point2[1]-point1[1])))/math.sqrt((math.pow(point2[0]-point1[0],2))+(math.pow(point2[1]-point1[1],2))))


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

# retrieves a point distant "distance" from "point", in the direction of "direction"
def getPointFromPoint(point, direction, distance):
    newX = int(math.floor(distance*math.cos(direction*(math.pi/180))+point[0]))
    newY = int(math.floor(-distance*math.sin(direction*(math.pi/180))+point[1]))
    return (newX,newY)
    
def slope(p1, p2):
    return (double(p2.getYCm()) - double(p1.getYCm()))/(double(p2.getXCm()) - double(p1.getXCm()))
