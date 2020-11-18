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
        
        print("Game modes: 1 = attack, 2 = defend, 3 = penalty (goals), 4 = penalty (kicker)")
        modeInput = raw_input("Enter game mode... ")
                

        #---------------- START PLANNING AND EXECUTING ---------------------------------
        try:
            if (modeInput == '1'):
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
                        
		                #comms.sendCmd(plan)
		                # time.sleep(15)	
                        if ((cmdsSent == 0 or comms.readSerial()=='d') and not(hasEnemyBall(beliefs)) and not(hasTeammateBall(beliefs)))
                            
                            
                            # ---------------------create plan to grab ball--------------------------
                            plan = planToGrab(beliefs)	
                            #--------DEBUG-------
                            #print("Plan to grab the ball: ")
                            #print(plan)
                            #print("our position is: "+str(beliefs.getMyPos()))
                            #print("our direction is: "+str(beliefs.getMyDirection()))
                            #print("our direction is: "+str(beliefs.getMyDirection()))
                            #print("the ball position is: "+str(beliefs.getBallPos()))
                            
                            if(len(plan)>2):
                                if(plan[2][0]=='f'):
                                    # if the plan is such that the second action is NOT 'gb','go' etc
                                    # then feed one command and keep on planning
                                    plan = plan[:2]

                            #-----------------------send command--------------------------------------
                            comms.sendCmd(plan)
                            print("sending "+str(plan))
                            #time.sleep(0.5)
                            cmdsSent+=1
                        else:
                            print("executing!") 
		            
                        #time.sleep(15)                
                        
                    if (cmdsSent == 0 or comms.readSerial() == 'd'):
                        plan = planToKick(beliefs)
                        print("Plan to kick the ball: ")
                        print(plan)
                        comms.sendCmd(plan)
                        time.sleep(1)

            elif(modeInput=='2'):
                beliefs.ball = self.eye.ball
                # ---------------------create plan to grab ball--------------------------
                plan = planToDefend(beliefs)	

                #-----------------------send command--------------------------------------
                comms.sendCmd(plan)
                print("sending "+str(plan))
                time.sleep(1)

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
