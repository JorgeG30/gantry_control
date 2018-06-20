#Import GPIO library to send signals to GPIO Pins to control motors
#Import time in order to control delay between stuff 
#Import keyboard in order to catch arrow key presses
from time import *
import keyboard
import pigpio


#Connect to pigpio daemon
pi = pigpio.pi()

#GPIO Pin assignments
XDIR = 20
XSTEP = 21
YDIR = 19
YSTEP = 16

#Direction Variables
CW = 1
CCW = 0

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

#Set initial duty cycles to 0 and pulses per second to 10
pi.set_PWM_frequency(XSTEP, 400)
pi.set_PWM_frequency(YSTEP, 400)

#Run a loop that when a certain button is pressed, manual control ends
while True:
	
	if keyboard.is_pressed('d'):
		pi.write(XDIR, CW)
		sleep(.1)
		pi.set_PWM_dutycycle(XSTEP, 128)
		sleep(.5)
		pi.set_PWM_dutycycle(XSTEP, 0)
		sleep(.1) 
		dC = dC + 1
	
	if keyboard.is_pressed('a'):
		pi.write(XDIR, CCW)
		sleep(.1)
		pi.set_PWM_dutycycle(XSTEP, 128)
		sleep(.5)
		pi.set_PWM_dutycycle(XSTEP, 0)
		sleep(.1)
		aC = aC + 1
		
	if keyboard.is_pressed('w'):
		pi.write(YDIR, CW)
		sleep(.1)
		pi.set_PWM_dutycycle(YSTEP, 128)
		sleep(.5)
		pi.set_PWM_dutycycle(YSTEP, 0)
		sleep(.1)
		wC = wC + 1
		
	if keyboard.is_pressed('s'):
		pi.write(YDIR, CCW)
		sleep(.1)
		pi.set_PWM_dutycycle(YSTEP, 128)
		sleep(.5)
		pi.set_PWM_dutycycle(YSTEP, 0)
		sleep(.1)
		sC = sC + 1
		
	if keyboard.is_pressed('esc'):
		break
		
	#currentTime = time()	
		
print 'Number of times s was pressed: ', sC
print 'Number of times a was pressed: ', aC
print 'Number of times w was pressed: ', wC
print 'Number of times d was pressed: ', dC
		
		
	





