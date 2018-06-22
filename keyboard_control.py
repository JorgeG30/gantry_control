#Import pigpio, time, and keyboard
from time import *
import pigpio
import keyboard
import rotary_encoder

#Connect to pigpio daemon
pi = pigpio.pi()

#GPIO Pin assignments
XDIR = 20
XSTEP = 21
YDIR = 19
YSTEP = 16
XA = 17
XB = 18

#Direction Variables
CW = 1
CCW = 0

#Define callback function for encoder
def XCallback(way):
	global xpos
	xpos = xpos + way

#Variables to hold the positions of the encoder and therefore the motor
xpos = 0
ypos = 0

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
		pi.write(YDIR, CW)
		pi.write(YSTEP, 1)
		pi.write(YSTEP, 0)
		sC = sC + 1
		
	if keyboard.is_pressed('w'):
		pi.write(YDIR, CCW)
		pi.write(YSTEP, 1)
		pi.write(YSTEP, 0)
		wC = wC + 1
		
	if keyboard.is_pressed('esc'):
		break	

print 'Number of times s was pressed: ', sC
print 'Number of times a was pressed: ', aC
print 'Number of times w was pressed: ', wC
print 'Number of times d was pressed: ', dC

print 'Encoder position: ', xpos


		
		
	





