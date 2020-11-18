#include "SDPArduino.h"
#include <Arduino.h>
#include <Wire.h>
#include <Servo.h>
#include <math.h>
#include "GeorgeConfig.h"
#include "SDPArduino.h"


Servo myservo;

#define ROTARY_SLAVE_ADDRESS 5
#define ROTARY_COUNT 6
#define PRINT_DELAY 200

// Initial motor position is 0.
int positions[ROTARY_COUNT] = {0};


//---------------------------------variables to calibrate movement and rotation-----------------------------
const double  turnRot = 1.45; // rotations for the prototype to spin of 1degree on its axis (value in deci seconds)
const double forwRot = 11.5;  // rotations for the prototype to move of one cm
const double slantRot = 13.4; // rotations for the prototype to move of one cm
const int kickHome = 0;
const int kickLifted = 55;




//------------------------------------------------------------------------------------------------------
//---------------------------Functions for rotary encoders to pick up rotations------------------------
void updateMotorPositions() {
  // Request motor position deltas from rotary slave board
  Wire.requestFrom(ROTARY_SLAVE_ADDRESS, ROTARY_COUNT);

  // Update the recorded motor positions
  for (int i = 0; i < ROTARY_COUNT; i++) {
    positions[i] += (int8_t) Wire.read();  // Must cast to signed 8-bit type
  }
}

void printMotorPositions() {
  Serial.print("Motor positions: ");
  for (int i = 0; i < ROTARY_COUNT; i++) {
    Serial.print(positions[i]);
    Serial.print(' ');
  }
  Serial.println();
  delay(PRINT_DELAY);  // Delay to avoid flooding serial out
}

//---------------------------------------------------------------------------------------------------------





//-----------------------------------------------------------------------------------------------------------
//-------------------------------Basic API with rotation encoders--------------------------------------------
// LEFT_MOTOR positon -->   positions[0]
// RIGHT_MOTOR position --> positions [1]
// REAR_MOTOR position --> positions [2]

void moveBackward(int cm) {
  memset(positions, 0, sizeof(positions));  // Set positions to zero
  int rotations = (int) floor(forwRot * cm);
  if (rotations < 0) {
    rotations = -rotations;
  }
  //Serial.println("..going backward");
  while (positions[0] < rotations || positions[1] < rotations) {
    if (positions[0] < rotations) {
      motorForward(LEFT_MOTOR, 100);
    }
    if (positions[1] < rotations) {
      motorForward(RIGHT_MOTOR, 100);
    }
    updateMotorPositions();
  }
  motorStop(RIGHT_MOTOR);
  motorStop(LEFT_MOTOR);
  //delay(300);
}

void moveForward(int cm) {
  memset(positions, 0, sizeof(positions));  // Set positions to zero
  int rotations = (int) floor(forwRot * cm);
  if (rotations < 0) {
    rotations = -rotations;
  }
  //Serial.println("..going forward");
//loopCount = 0;  
while (-positions[0] < rotations || -positions[1] < rotations) {
    if (-positions[0] < rotations) {
      motorBackward(LEFT_MOTOR, 100);
    }
    if (-positions[1] < rotations) {
      motorBackward(RIGHT_MOTOR, 100);
    }
    updateMotorPositions();
    
    //LUCA CHECK THIS !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ***********
    
//    if (loopCount >= 100 && -positions[0] < rotations || -positions[1] < rotations){
//    	motorStop(RIGHT_MOTOR);
//  	motorStop(LEFT_MOTOR);    
 //   }
  }
  memset(positions, 0, sizeof(positions));  // Set positions to zero
  motorStop(RIGHT_MOTOR);
  motorStop(LEFT_MOTOR);
  //delay(300);
}

void slantRight(int cm) {
  memset(positions, 0, sizeof(positions));  // Set positions to zero
  int rotations = (int) floor(slantRot * cm);
  if (rotations < 0) {
    rotations = -rotations;
  }
  //Serial.println("..slanting right");
  while (-positions[2] < rotations) {
    motorBackward(REAR_MOTOR, 100);
    updateMotorPositions();
  }
  memset(positions, 0, sizeof(positions));  // Set positions to zero
  motorStop(REAR_MOTOR);
  //delay(300);
  };


void slantLeft(int cm) {
  int rotations = (int) floor(slantRot * cm);
  if (rotations < 0) {
    rotations = -rotations;
  }
  //Serial.println("..slanting left");
  while (positions[2] < rotations) {
    motorForward(REAR_MOTOR, 100);
    updateMotorPositions();
  }
  memset(positions, 0, sizeof(positions));  // Set positions to zero
  motorStop(REAR_MOTOR);
  //delay(300);
  };    // slanted motion (to be implemented)

void turnLeft(int deg) {
  /*sl*/
  int rotations = (int) floor(turnRot * deg);
  if (rotations < 0) {
    rotations = -rotations;
  }
  //Serial.println("..going left");
  memset(positions, 0, sizeof(positions));  // Set positions to zero
  while ((positions[0] < rotations || -positions[1] < rotations) || positions[2]<rotations) {
// ----DEBUG----  
//    delay(200);
//    Serial.print(positions[0]);
//    Serial.print(" ");
//    Serial.print(positions[1]);
//    Serial.print(" ");
//    Serial.print(positions[2]);
//    Serial.println();
    if (positions[0] < rotations) {
      motorForward(LEFT_MOTOR, 70);
    }
    else{
      motorStop(LEFT_MOTOR);
    }
    if (-positions[1] < rotations) {
      motorBackward(RIGHT_MOTOR, 70);
    }
    else{
      motorStop(RIGHT_MOTOR);
    }
    if(positions[2]<rotations){
      motorForward(REAR_MOTOR, 70);
    }
    else{
      motorStop(REAR_MOTOR);
    }
    updateMotorPositions();
  }
  memset(positions, 0, sizeof(positions));  // Set positions to zero
  motorStop(RIGHT_MOTOR);
  motorStop(LEFT_MOTOR);
  motorStop(REAR_MOTOR);
  //delay(300);
}

void turnRight(int deg) {
  memset(positions, 0, sizeof(positions));  // Set positions to zero
  int rotations = (int) floor(turnRot * deg);
  if (rotations < 0) {
    rotations = -rotations;
  }
  //Serial.println("..going right");
  while ((-positions[0] < rotations || positions[1] < rotations) || -positions[2]<rotations) {
//    delay(200);
//    Serial.print(positions[0]);
//    Serial.print(" ");
//    Serial.print(positions[1]);
//    Serial.print(" ");
//    Serial.print(positions[2]);
//    Serial.println();
    if (-positions[0] < rotations) {
      motorBackward(LEFT_MOTOR, 70);
    }
    else{
      motorStop(LEFT_MOTOR);
    }
    if (positions[1] < rotations) {
      motorForward(RIGHT_MOTOR, 70);
    }
    else{
      motorStop(RIGHT_MOTOR);
    }
    if(-positions[2]<rotations){
      motorBackward(REAR_MOTOR, 70);
    }
    else{
      motorStop(REAR_MOTOR);
    }
    updateMotorPositions();
  }
  memset(positions, 0, sizeof(positions));  // Set positions to zero
  motorStop(RIGHT_MOTOR);
  motorStop(LEFT_MOTOR);
  motorStop(REAR_MOTOR);
  //delay(300);
}


void kick(int cm) {

  myservo.attach(9);
  myservo.write(0); //home position

  // variables to convers cm linearly to delay milliseconds
  double conversionWeight = -.15;
  double conversionOffset = 26.5;

  int kickDelay = 1;
  //Serial.print("..kicking");
  if (cm<150){
    kickDelay = (int) floor(-cm*(.17)+conversionOffset);
  }
  Serial.print(kickDelay);
  for (int pos = kickHome; pos <= kickLifted; pos += 1) { // goes from 0 degrees to 180 degrees
    // in steps of 1 degree
    myservo.write(pos);
    delay(kickDelay);                //controls how fast the kick
  }
  delay(1000);
  for (int pos = kickLifted; pos >= kickHome; pos -= 1) { // goes from 180 degrees to 0 degrees
    myservo.write(pos);
    //delay(kickDelay);
    delay(15);
  }
  //delay(300);

};

void grabRelease(){
    //Serial.print("open grabber");
    motorForward(GRAB_MOTOR, 100);
    delay(480);
    motorStop(GRAB_MOTOR);
}

void grab(){
    //Serial.print("close grabber");
    motorBackward(GRAB_MOTOR, 100);
    delay(600);
    motorStop(GRAB_MOTOR);
    delay(300);
}

void grabBall(){
  grabRelease();
  motorBackward(LEFT_MOTOR, 80);
  motorBackward(RIGHT_MOTOR, 80);
  delay(950);
  grab();
  motorStop(LEFT_MOTOR);
  motorStop(RIGHT_MOTOR);
  //delay(300);
}
