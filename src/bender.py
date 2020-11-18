from threading import Thread, Event
import time
from eyes import Eye
from planning_functions import *
from base import *
from cmd_sender import Comms
import sys
import yaml
import argparse
import copy

vision = True
debug = False
go = False

class PlanLoop:
    def __init__(self, conf):
        self.conf = conf
    def begin(self):
	cmdsSent = 0
        # This event is triggered when the preprocessing is completed
        self.startedFeed = Event()

        beliefs = State()
        comms = Comms(self.conf['CommsPort'], 115200)
        
        #----------CONFIGURATION FOR THE GAME--------------------------------------
        # Adds the goals from the config file
        defend = self.conf['Goals']['defend']
        beliefs.goalToDefend = Goal(defend[0], defend[1], name='defend')
        attack = self.conf['Goals']['attack']
        beliefs.goalToScore = Goal(attack[0], attack[1], True, name='attack')

        # Identify and create the robots from config file information
        teamColour = self.conf['Teams']['allies']
        enemyColour = self.conf['Teams']['enemies']

        myColour = self.conf['MyColour']
        allyColour = [color for color in self.conf['UnitColours'] if color != myColour][0]

        beliefs.me = Robot(0, 0,0, 0, '{}'.format(teamColour[0]+myColour[0]))
        beliefs.teammate = Robot(0, 0, 0, 0, '{}'.format(teamColour[0]+allyColour[0]))

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
        #----------------------------------------------------------------------------
        
        #------------------ VISION FEED ---------------------------------------------
        self.eye = Eye(beliefs, self.startedFeed)

        # Starts the vision thread
        if vision:
            self.look = Thread(target=self.eye.startLooking)
            self.look.start()
        else:
            beliefs.ball = Ball(0,0,10,1,5, name='ball')
            self.startedFeed.set()

        if not debug:
            # Wait for the feed to start up and preprocess
            self.startedFeed.wait()

        plan = []
        #workingBeliefs = copy.deepcopy(self.eye.beliefs)
        time.sleep(3)
        
        print("Game modes: 1 = attack, 2 = defend, 3 = penalty (goals), 4 = penalty (kicker), 5 = Play game with kickoff")
        modeInput = raw_input("Enter game mode... ")
                

        #---------------- START PLANNING AND EXECUTING ---------------------------------
        try:
            if (modeInput == '1' or '5'):
                if (modeInput == '5'):
                    beliefs.ball = self.eye.ball
                    plan = planToKickOff(beliefs)
                    comms.sendCmd(plan)
                    print("kicking off...")
                while True:
                    beliefs.ball = self.eye.ball
                    #-----------------------------------------------------
                    #------DEBUG!-----------
                    #print("our position is: "+str(beliefs.getMyPos()))
                    #print("our direction is: "+str(beliefs.getMyDirection()))
                    #print("the ball position is: "+str(beliefs.getBallPos()))
                    #-----------------------------------------------------
                
                    while(not(haveWeBall(beliefs))):
                        
                        #print("distance from the ball is: "+str(ballDistance))
                        #print("Partial plan that it is executing at this iteration: ")
                        #print(plan)
                        
                        #--------PLAN TO DEFEND FROM A PASS------	
                        if (hasEnemyBall(beliefs) and (cmdsSent == 0 or comms.readSerial()=='d')):
                            plan = planToDefend(beliefs)	
                            if(len(plan)>2):
                                if(plan[2][0]=='f' or plan[2][0]=='b'):
                                    plan = plan[:2]
                            
                            #----send command--------
                            comms.sendCmd(plan)
                            print("Trying to defend. Sending: "+str(plan))
                            #time.sleep(0.5)
                            cmdsSent+=1
                        
                        #--------PLAN TO RECEIVE FROM TEAMMATE------	
                        elif (hasTeammateBall(beliefs) and (cmdsSent == 0 or comms.readSerial()=='d')):    
                            plan = planToReceivePass(beliefs)
                            
                            #----send command--------
                            comms.sendCmd(plan)
                            print("Trying to defend. Sending: "+str(plan))
                            #time.sleep(0.5)
                            cmdsSent+=1
                            
		                #--------PLAN TO GRAB------	
                        elif(cmdsSent == 0 or comms.readSerial()=='d'):
                            # ---------------------create plan to grab ball--------------------------
                            plan = planToGrab(beliefs)	
                            #--------DEBUG-------
                            #print("Plan to grab the ball: ")
                            #print(plan)
                            print("our position is: "+str(beliefs.getMyPos()))
                            print("our direction is: "+str(beliefs.getMyDirection()))
                            print("the ball position is: "+str(beliefs.getBallPos()))
                            print("Plan to grab the ball: ")
                            print(plan)
                            print(beliefs.getMyPos())
                            if(len(plan)>2):
                                if(plan[2][0]=='f' or plan[2][0]=='b'):
                                    # if the plan is such that the second action is NOT 'gb','go' etc
                                    # then feed one command and keep on planning
                                    plan = plan[:2]

                            #-----------------------send command--------------------------------------
                                comms.sendCmd(plan)
                                print("Trying to grab the ball. Sending "+str(plan))
                                #time.sleep(0.5)
                                cmdsSent+=1
                        else:
                            print("executing!") 
		            
                        #time.sleep(15)                
                        
                    #--------PLAN TO KICK INTO GOAL------
                    goalPosition = (0,100)
                    if(beliefs.getGoalToScore()[0]==0):
                        goalPosition = (0,100)
                    else:
                        goalPosition = (300,100)
                    dirToReach = angleToPoint(beliefs.getMyPos(), goalPosition)
                    while(not(reachedDirection(beliefs.getMyDirection(),dirToReach)) and haveWeBall(beliefs)):
                        if(cmdsSent == 0 or comms.readSerial()=='d'):
                            print("trying to turn")
                            plan = [planToTurn(beliefs.getMyDirection(),dirToReach)]
                            comms.sendCmd(plan)
                            cmdsSent+=1
                        myDirection = beliefs.getMyDirection()
                        myPosition = beliefs.getMyPos()
                        dirToReach = angleToPoint(myPosition, goalPosition)
                    cmdsSent = 0
                    if(comms.readSerial()=='d'):
                        print("Trying to kick the ball. ")
                        plan = ['go','k150','gc']
                        comms.sendCmd(plan)
                        cmdsSent+=1
                        time.sleep(1)

            elif(modeInput=='2'):
                while True:
                    if(cmdsSent == 0 or comms.readSerial()=='d'):
                        plan = planToDefend(beliefs)	
                        if(len(plan)>2):
                            if(plan[2][0]=='f'):
                                plan = plan[:2]
                        
                        #-----------------------send command--------------------------------------
                        comms.sendCmd(plan)
                        print("Trying to defend. Sending: "+str(plan))
                        #time.sleep(0.5)
                        cmdsSent+=1
                    if (dist(beliefs.getBallPos(),beliefs.getMyPos())>25):
                        break

            elif(modeInput=='3'):
                initialBallPosition = beliefs.getBallPos()
                defended = False
                while not(defended):
                    currentBallPosition = beliefs.getBallPos()
                    posChange = dist(initialBallPosition,currentBallPosition)
                    print(posChange)
                    if(posChange>2):
                        comms.sendCmd(['go'])
                        defended = True
                time.sleep(3)
                plan = ['gc']
                comms.sendCmd(plan)
                while (not(haveWeBall(beliefs))):
                    if (comms.readSerial() == 'd'):

                        # ---------------------create plan to grab ball--------------------------
                        plan = planToGrab(beliefs)	
                        if(len(plan)>2):
                            if(plan[2][0]=='f'):
                                plan = plan[:2]

                        #-----------------------send command--------------------------------------
                        comms.sendCmd(plan)
                    else:
                        print("executing!")
                comms.closePort()
                self.eye.terminate()
                
            elif(modeInput=='4'):
                plan = ['r4','go','k150','gc']
                plan = ['r10','go','k150','gc']
                comms.sendCmd(plan)
                comms.closePort()
                self.eye.terminate()
                
            else:
                comms.closePort()
                comms.closePort()
                self.eye.terminate()
                
        except KeyboardInterrupt:
            comms.closePort()
            self.eye.terminate()

            
            
        #-------------------------------------------------------------------------------

def main():
    conf = yaml.load(file('setup.yaml').read())
    #mouth = Comms(conf['CommsPort'], 115200)
    mouth = Comms('/dev/ttyACM0', 115200)
    bender = PlanLoop(conf)
    bender.begin()

if __name__ == '__main__':
    main()
