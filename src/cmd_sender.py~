import serial
import time

cmdExamples = [['r90', 'f50', 'l90', 'f50'],
['', 'f99', 'r135', 'go'],
['r90', 'f40', 'l90', 'f49', 'l90', 'go', 'k150', 'gc'],
['l90', 'f10', 'r90', 'f25', 'l180', 'go', 'k50', 'gc']]


class Comms:
    def __init__(self, serialPort, baud):
        self.ser = serial.Serial(serialPort, baud)

    def formatCmd(self,cmd):
        cmdString = ','.join(cmd)
	if len(cmdString)>0:
            if cmdString[0] == ',':
                cmdString = cmdString[1:]
        cmdCount = len(cmdString.split(','))
        cmdString += ',\r'
        return cmdString


    def sendRawCmd(self, cmd):
        for byte in cmd:
            time.sleep(0.033)
            self.ser.write(byte)

    def sendCmd(self, cmd):

        cmdFormatted = self.formatCmd(cmd)
        self.sendRawCmd(cmdFormatted)

    def closePort(self):
        self.ser.close()

    def readSerial(self):
        msg = self.ser.read(1)
	return msg
    
    def flushSerialIn(self):
	self.ser.flushInput()
	
    def flushSerialOut(self):
        self.ser.flushOutput()
	


def main():
    filename = raw_input("Enter the name of the file to be transmitted: ")
    comms = Comms("/dev/cu.usbmodem000001", 115200)

    for command in cmdExamples:
        cmdFormatted = comms.formatCmd(cmdExamples[1])
        comms.sendCmd(cmdFormatted)
    print "sent command!"

    time.sleep(2)

if __name__ == '__main__':
    main()
