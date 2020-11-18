#include "Arduino.h"
#include <Servo.h>

Servo myservo;  

int pos = 0;

void setup() {
  myservo.attach(9);
  myservo.write(0); //home position
  //delay(500);
  //myservo.write(-50);
  
}

void loop() {
  /*UP*/
  /*for (pos = 125; pos >= 95; pos -= 1) { // goes from 180 degrees to 0 degrees
    myservo.write(pos);              // tell servo to go to position in variable 'pos'
    delay(1);                       // waits 15ms for the servo to reach the position
  }
  delay(3000);
  /*DOWN*/
  /*for (pos = 95; pos <= 125; pos += 1) { 
    // in steps of 1 degree
    myservo.write(pos);              // tell servo to go to position in variable 'pos'
    delay(15);                       // waits 15ms for the servo to reach the position
  }
  delay(3000);*/
 
}

//50cm = 15ms delay
//100cm = 7ms delay
//150cm = 1ms delay


