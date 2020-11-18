
Project Authors:

 - Luca Scimeca
 - Sam Rust
 - Steven Heggie
 - Bence Karpati
 - Prateek Bawa
 - Dhonnald O'shea



# SDP GROUP 6-C USER MANUAL 2016

## General Operator Information

### Introduction
The purpose of this project is to build and operational robot in accordance with 
the specification provided by the 2016 SDP coursework.
The robot is built with Arduino and is capable of playing a 2 a side football match.
The repo contains the Arduino code, a Python planner and visual processing code for
the camera feed.


### 1.2 Command Structure

Basic structure of commands:
- fn, : move _robot_ forward n centimeteres.
- bn, : move _robot_ backward n centimeteres.
- ln, : move _robot_ left n degrees.
- rn, : move _robot_ right n degrees.
- sln, : slant _robot_ left of n cm.
- srn, : slant _robot_ right of n cm.
- go, : open grabber.
- gc, : close grabber.
- gb, : grab ball.
- kn, : _robot_ kicks ball n cm.

Comma terminates command. '\r' terminates command sequence.
_robot_ executes command sequence as a batch job all at once.

the commands can be executed from the Arduino command line