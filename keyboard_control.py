#Import pigpio, time, and keyboard
from time import *
import pigpio
import keyboard
import rotary_encoder

#Connect to pigpio daemon
pi = pigpio.pi()

#GPIO Pin assignments
XDIR = 20
XSTEP = 12
YDIR = 19
YSTEP = 13
XA = 5
XB = 17
YA = 25
YB = 22
notYA = 27 
notYB = 23  
notXA = 6
notXB = 18 
readX = 24
readY = 21


#Direction Variables
CW = 1
CCW = 0

#Define callback functions for encoders
def XCallback(way):
	global xpos
	xpos = xpos + way
	
def YCallback(way):
	global ypos
	ypos = ypos + way
	
def notXCallback(way):
	global notXpos
	notXpos = notXpos + way
	
def notYCallback(way):
	global notYpos
	notYpos = notYpos + way
	
#Define callback functions for pulses
def XPulse(gpio, level, tick):
	global xPulses
	xPulses = xPulses + 1
	
def YPulse(gpio, level, tick):
	global yPulses
	yPulses = yPulses + 1

#Variables to hold the positions of the encoder and therefore the motor
xpos = 0
ypos = 0
notXpos = 0
notYpos = 0

#Pulses per 1mm
x_pulses_per_mm = 92
y_pulses_per_mm = 119

#Set up pins as outputs
pi.set_mode(XDIR, pigpio.OUTPUT)
pi.set_mode(XSTEP, pigpio.OUTPUT)
pi.set_mode(YDIR, pigpio.OUTPUT)
pi.set_mode(YSTEP, pigpio.OUTPUT)

#Counter for button presses
aC = 0
sC = 0
dC = 0
wC = 0
	
#Initialize decoders for X and Y encoders
XDecoder = rotary_encoder.decoder(pi, XA, XB, XCallback)
YDecoder = rotary_encoder.decoder(pi, YA, YB, YCallback)
notXDecoder = rotary_encoder.notDecoder(pi, notXA, notXB, notXCallback)
notYDecoder = rotary_encoder.notDecoder(pi, notYA, notYB, notYCallback)

#Initialize pulse variables to 0 and create callbacks
xPulses = 0
yPulses = 0
cb1 = pi.callback(readX, pigpio.RISING_EDGE, XPulse)
cb2 = pi.callback(readY, pigpio.RISING_EDGE, YPulse)

#Run a loop that ends when enter is pressed, manual control ends
#W is UP, S is down, A is left. D is right
while True:
	
	if keyboard.is_pressed('d'):
		pi.write(XDIR, CW)
		pi.write(XSTEP, 1)
		pi.write(XSTEP, 0)
		dC = dC + 1
		 
	if keyboard.is_pressed('a'):
		pi.write(XDIR, CCW)
		pi.write(XSTEP, 1)
		pi.write(XSTEP, 0)
		aC = aC + 1

	if keyboard.is_pressed('s'):
		pi.write(YDIR, CCw)
		pi.write(YSTEP, 1)
		pi.write(YSTEP, 0)
		sC = sC + 1
		
	if keyboard.is_pressed('w'):
		pi.write(YDIR, CW)
		pi.write(YSTEP, 1)
		pi.write(YSTEP, 0)
		wC = wC + 1
		
	if keyboard.is_pressed('esc'):
		break
	
	#Calculate position of Gantry based on Pulses sent
	left = float(aC)/float(x_pulses_per_mm)
	right = float(dC)/float(x_pulses_per_mm)
	up = float(wC)/float(y_pulses_per_mm)
	down = float(sC)/float(y_pulses_per_mm)
	
	currentX = float(right) - float(left)
	currentY = float(up) - float(down)
	
	print 'Current Position: (%f, %f)' % (currentX, currentY)

#Calculate position of Gantry based on Pulses sent
currentX = 0
currentY = 0
left = aC/x_pulses_per_mm
right = dC/x_pulses_per_mm
up = wC/y_pulses_per_mm
down = sC/y_pulses_per_mm

currentX = right - left
currentY = up - down



print 'Number of times s was pressed: ', sC
print 'Number of times a was pressed: ', aC
print 'Number of times w was pressed: ', wC
print 'Number of times d was pressed: ', dC

print 'X Encoder position: ', xpos
print 'Y Encoder position: ', ypos
print 'Not X Encoder position: ', notXpos
print 'Not Y Encoder position: ', notYpos

print 'Number of X pulses: ', xPulses
print 'Number of Y pulses: ', yPulses

print 'Current Position: (%d, %d)' % (currentX, currentY)





		
		
	





