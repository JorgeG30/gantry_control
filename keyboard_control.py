#Import GPIO library to send signals to GPIO Pins to control motors
#Import time in order to control delay between stuff 
#Import keyboard in order to catch arrow key presses
from time import *
import RPi.GPIO as GPIO
import keyboard

#GPIO PIn assignments
XDIR = 20
XSTEP = 21
YDIR = 19
YSTEP = 16

#Direction Variables
CW = 1
CCW = 0

#Steps per Revolution based on ST M5405 Manual
SPR = 64 


GPIO.setmode(GPIO.BCM)
GPIO.setup(XDIR, GPIO.OUT)
GPIO.setup(YDIR, GPIO.OUT)
GPIO.setup(XSTEP, GPIO.OUT)
GPIO.setup(YSTEP, GPIO.OUT)

#Counter for button presses
aC = 0
sC = 0
dC = 0
wC = 0

#Set the delay between high and low on the
delay = 1/SPR

currentTime = time()
endTime = currentTime + 10

#Run a loop that when a certain button is pressed, manual control ends
while currentTime < endTime + 10:
	
	if keyboard.is_pressed('d'):
		GPIO.output(XDIR, CW)
		GPIO.output(XSTEP, GPIO.HIGH)
		sleep(delay)
		GPIO.output(XSTEP, GPIO.LOW)
		sleep(delay) 
		dC = dC + 1
	
	if keyboard.is_pressed('a'):
		GPIO.output(XDIR, CCW)
		GPIO.output(XSTEP, GPIO.HIGH)
		sleep(delay)
		GPIO.output(XSTEP, GPIO.LOW)
		sleep(delay)
		aC = aC + 1
		
	if keyboard.is_pressed('w'):
		GPIO.output(YDIR, CW)
		GPIO.output(YSTEP, GPIO.HIGH)
		sleep(delay)
		GPIO.output(YSTEP, GPIO.LOW)
		sleep(delay)
		wC = wC + 1
		
	if keyboard.is_pressed('s'):
		GPIO.output(YDIR, CCW)
		GPIO.output(YSTEP, GPIO.HIGH)
		sleep(delay)
		GPIO.output(YSTEP, GPIO.LOW)
		sleep(delay)
		sC = sC + 1
		
	currentTime = time()	
		
print 'Number of times s was pressed: ', sC
print 'Number of times a was pressed: ', aC
print 'Number of times w was pressed: ', wC
print 'Number of times d was pressed: ', dC
		
		
	





