import unittest
from planning_functions import *
from base import *

class TestPlanningFunctions(unittest.TestCase):

#-------------------- TEST ----------------------------------
#State has to be initialized as below
#(me=Robot(x,y,direction,magnitude),teammate=Robot(x,y,direction,magnitude),adv1=Robot(x,y,direction,magnitude),adv2=Robot#(x,y,direction,magnitude),ball=Ball(x,y,size,direction,magnitude), goalToScore=Goal(x,y,True),goalToDefend=Goal(x,y))

    def test_1(self):
        #---------------------
        bender = Robot(0,0,0,0)
        bender.setXPixel(75)
        bender.setYPixel(170)
        #---------------------
        teammate = Robot(0,0,-0,0)
        teammate.setXPixel(150)
        teammate.setYPixel(100)
        #---------------------
        adv1 = Robot(0,0,-90,0)
        adv1.setXPixel(200)
        adv1.setYPixel(100)
        #---------------------
        adv2 = Robot(0,0,0,0)
        adv2.setXPixel(300)
        adv2.setYPixel(100)
        #---------------------
        ball = Ball(0,0,20,90,0)
        ball.setXPixel(75)
        ball.setYPixel(30)
        #---------------------
        goalToScore = Goal(0,0,True)
        goalToScore.setXPixel(300)
        goalToScore.setYPixel(100)
        #---------------------
        goalToDefend = Goal(0,0)
        goalToDefend.setXPixel(0)
        goalToDefend.setYPixel(100)
        #---------------------
        state = State(bender,teammate,adv1,adv2,ball,goalToScore,goalToDefend)
        result = planToGrab(state)
        correctResult = ['l90', 'f50', 'f50', 'f10', 'gb']
        self.assertEqual(correctResult, result)

    def test_2(self):
        #---------------------
        bender = Robot(0,0,45,0)
        bender.setXPixel(50)
        bender.setYPixel(170)
        #---------------------
        teammate = Robot(0,0,-0,0)
        teammate.setXPixel(150)
        teammate.setYPixel(100)
        #---------------------
        adv1 = Robot(0,0,-90,0)
        adv1.setXPixel(200)
        adv1.setYPixel(100)
        #---------------------
        adv2 = Robot(0,0,0,0)
        adv2.setXPixel(300)
        adv2.setYPixel(100)
        #---------------------
        ball = Ball(0,0,20,90,0)
        ball.setXPixel(250)
        ball.setYPixel(170)
        #---------------------
        goalToScore = Goal(0,0,True)
        goalToScore.setXPixel(300)
        goalToScore.setYPixel(100)
        #---------------------
        goalToDefend = Goal(0,0)
        goalToDefend.setXPixel(0)
        goalToDefend.setYPixel(100)
        #---------------------
        state = State(bender,teammate,adv1,adv2,ball,goalToScore,goalToDefend)
        result = planToGrab(state)
        correctResult = ['r45', 'f50', 'f50', 'f50', 'f20', 'gb']
        self.assertEqual(correctResult, result)

    def test_3(self):
        #---------------------
        bender = Robot(0,0,-135,0)
        bender.setXPixel(225)
        bender.setYPixel(150)
        #---------------------
        teammate = Robot(0,0,-0,0)
        teammate.setXPixel(150)
        teammate.setYPixel(100)
        #---------------------
        adv1 = Robot(0,0,-90,0)
        adv1.setXPixel(200)
        adv1.setYPixel(100)
        #---------------------
        adv2 = Robot(0,0,0,0)
        adv2.setXPixel(300)
        adv2.setYPixel(100)
        #---------------------
        ball = Ball(0,0,20,90,0)
        ball.setXPixel(250)
        ball.setYPixel(50)
        #---------------------
        goalToScore = Goal(0,0,True)
        goalToScore.setXPixel(300)
        goalToScore.setYPixel(100)
        #---------------------
        goalToDefend = Goal(0,0)
        goalToDefend.setXPixel(0)
        goalToDefend.setYPixel(100)
        #---------------------
        state = State(bender,teammate,adv1,adv2,ball,goalToScore,goalToDefend)
        result = planToGrab(state)
        correctResult = ['l31', 'b50', 'b23', 'l179', 'gb']
        self.assertEqual(correctResult, result)
          
    def test_4(self):
        #---------------------
        bender = Robot(0,0,45,0)
        bender.setXPixel(225)
        bender.setYPixel(50)
        #---------------------
        teammate = Robot(0,0,-0,0)
        teammate.setXPixel(150)
        teammate.setYPixel(100)
        #---------------------
        adv1 = Robot(0,0,-90,0)
        adv1.setXPixel(200)
        adv1.setYPixel(100)
        #---------------------
        adv2 = Robot(0,0,0,0)
        adv2.setXPixel(300)
        adv2.setYPixel(100)
        #---------------------
        ball = Ball(0,0,20,90,0)
        ball.setXPixel(75)
        ball.setYPixel(150)
        #---------------------
        goalToScore = Goal(0,0,True)
        goalToScore.setXPixel(300)
        goalToScore.setYPixel(100)
        #---------------------
        goalToDefend = Goal(0,0)
        goalToDefend.setXPixel(0)
        goalToDefend.setYPixel(100)
        #---------------------
        state = State(bender,teammate,adv1,adv2,ball,goalToScore,goalToDefend)
        result = planToGrab(state)
        correctResult = ['r11', 'b50', 'b50', 'b50', 'b1', 'r179', 'gb']
        self.assertEqual(correctResult, result)
      
    def test_5(self):
        #---------------------
        bender = Robot(0,0,45,0)
        bender.setXPixel(75)
        bender.setYPixel(150)
        #---------------------
        teammate = Robot(0,0,-0,0)
        teammate.setXPixel(150)
        teammate.setYPixel(100)
        #---------------------
        adv1 = Robot(0,0,-90,0)
        adv1.setXPixel(200)
        adv1.setYPixel(100)
        #---------------------
        adv2 = Robot(0,0,0,0)
        adv2.setXPixel(300)
        adv2.setYPixel(100)
        #---------------------
        ball = Ball(0,0,20,90,0)
        ball.setXPixel(225)
        ball.setYPixel(195)
        #---------------------
        goalToScore = Goal(0,0,True)
        goalToScore.setXPixel(300)
        goalToScore.setYPixel(100)
        #---------------------
        goalToDefend = Goal(0,0)
        goalToDefend.setXPixel(0)
        goalToDefend.setYPixel(100)
        #---------------------
        state = State(bender,teammate,adv1,adv2,ball,goalToScore,goalToDefend)
        result = planToGrab(state)
        correctResult = ['r50', 'f50', 'f50', 'f50', 'f1', 'r10', 'gb']
        self.assertEqual(correctResult, result)
      
    def test_6(self):
        #---------------------
        bender = Robot(0,0,90,0)
        bender.setXPixel(75)
        bender.setYPixel(50)
        #---------------------
        teammate = Robot(0,0,-0,0)
        teammate.setXPixel(150)
        teammate.setYPixel(100)
        #---------------------
        adv1 = Robot(0,0,-90,0)
        adv1.setXPixel(200)
        adv1.setYPixel(100)
        #---------------------
        adv2 = Robot(0,0,0,0)
        adv2.setXPixel(300)
        adv2.setYPixel(100)
        #---------------------
        ball = Ball(0,0,20,90,0)
        ball.setXPixel(292)
        ball.setYPixel(150)
        #---------------------
        goalToScore = Goal(0,0,True)
        goalToScore.setXPixel(300)
        goalToScore.setYPixel(100)
        #---------------------
        goalToDefend = Goal(0,0)
        goalToDefend.setXPixel(0)
        goalToDefend.setYPixel(100)
        #---------------------
        state = State(bender,teammate,adv1,adv2,ball,goalToScore,goalToDefend)
        result = planToGrab(state)
        correctResult = ['l61', 'b50', 'b50', 'b50', 'b50', 'b12', 'r176', 'gb']
        self.assertEqual(correctResult, result)
     
     
# NOTE: this test will only pass if in the 'setyp.yaml' file -> defend = [0, 100]
    def test_7(self):
        #---------------------
        bender = Robot(0,0,90,0)
        bender.setXPixel(75)
        bender.setYPixel(50)
        #---------------------
        teammate = Robot(0,0,-0,0)
        teammate.setXPixel(150)
        teammate.setYPixel(100)
        #---------------------
        adv1 = Robot(0,0,-90,0)
        adv1.setXPixel(200)
        adv1.setYPixel(100)
        #---------------------
        adv2 = Robot(0,0,0,0)
        adv2.setXPixel(255)
        adv2.setYPixel(155)
        #---------------------
        ball = Ball(0,0,20,90,0)
        ball.setXPixel(250)
        ball.setYPixel(150)
        #---------------------
        goalToScore = Goal(0,0,True)
        goalToScore.setXPixel(300)
        goalToScore.setYPixel(100)
        #---------------------
        goalToDefend = Goal(0,0)
        goalToDefend.setXPixel(0)
        goalToDefend.setYPixel(100)
        #---------------------
        state = State(bender,teammate,adv1,adv2,ball,goalToScore,goalToDefend)
        result = planToDefend(state)
        correctResult = ['r41', 'b50', 'b17', 'r60']
        self.assertEqual(correctResult, result)

    def test_8(self):
        #---------------------
        bender = Robot(0,0,180,0)
        bender.setXPixel(75)
        bender.setYPixel(50)
        #---------------------
        teammate = Robot(0,0,-0,0)
        teammate.setXPixel(150)
        teammate.setYPixel(150)
        #---------------------
        adv1 = Robot(0,0,-90,0)
        adv1.setXPixel(200)
        adv1.setYPixel(100)
        #---------------------
        adv2 = Robot(0,0,0,0)
        adv2.setXPixel(255)
        adv2.setYPixel(155)
        #---------------------
        ball = Ball(0,0,20,90,0)
        ball.setXPixel(250)
        ball.setYPixel(150)
        #---------------------
        goalToScore = Goal(0,0,True)
        goalToScore.setXPixel(300)
        goalToScore.setYPixel(100)
        #---------------------
        goalToDefend = Goal(0,0)
        goalToDefend.setXPixel(0)
        goalToDefend.setYPixel(100)
        #---------------------
        state = State(bender,teammate,adv1,adv2,ball,goalToScore,goalToDefend)
        result = planToReceivePass(state)
        correctResult = ['l126']
        self.assertEqual(correctResult, result)
        
if __name__ == '__main__':
    unittest.main()