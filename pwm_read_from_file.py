#Import pigpio, time, and keyboard
from time import *
import pigpio
import keyboard
import rotary_encoder
import csv

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

#Set Pulse counters to 0
xPulseCount = 0
yPulseCount = 0
xPulses = 0
yPulses = 0

#Set direction to default to CW
direction = CW

#Create pulse callback functions to keep track of total number of pulses sent
def XPulse(gpio, level, tick):
	global xPulses
	global xdir
    global ydir
    global currentY
    global currentX
    xfreq = 92
    yfreq = 119
	if xdir == 0:
		xPulses = xPulses - 1
	elif xdir == 1:
		xPulses = xPulses + 1
    currentX = currentY
    #Print current coordinate each time function is called
    currentX = xPulses/xfreq
    print 'Current location: (%f, %f)' % (currentX, currentY)

def YPulse(gpio, level, tick):
	global yPulses
	global ydir
    global xdir
    global currentY
    global currentX
    xfreq = 92
    yfreq = 119
	if ydir == 0:
		yPulses = yPulses - 1
	elif ydir == 1:
		yPulses = yPulses + 1
    currentY = yPulses/yfreq
    print 'Current location: (%f, %f)' % (currentX, currentY)
        
cb1 = pi.callback(readX, pigpio.RISING_EDGE, XPulse)
cb2 = pi.callback(readY, pigpio.RISING_EDGE, YPulse)   

def findDirection(distance):
    
    #Variable that will be modified 
    if distance > 0:
        direction = CW
    elif distance < 0:
        direction = CCW
	
#Functions for going to a certain X or Y
def gotoXY(currX, currY, nextX, nextY):
	
	#Variable for speed
	#speed = input('Enter your desired speed')
	
	#Variable that stores the frequencies
	xfreq = 92
	yfreq = 119
    
    #Global variable that will store the directions of x and y
    global xdir
    global ydir
	
	#Calculate the distance between the current and next points
	xdist = nextX - currX
	ydist = nextY - currY
    
    #Set separate delays for X and Y
    xdelay = 1
    ydelay = 1
    
    #Determine the direction using direction function
	xdir = findDirection(xdist)
    ydir = findDirection(ydist)
    
    #Write to GPIO pins
    pi.write(XDIR, xdir)
    pi.write(YDIR, ydir)
    
    #Start PWM 
    
    """"
    If there is less distance to cover in the x direction
    Have both X and Y PWM go until X is finished, then finish
    whatever is leftover in the Y distance to cover
    else do the opposite
    """"
    if xdist < ydist:
        
        pi.hardware_PWM(XSTEP, xfreq, 500000)
        pi.hardware_PWM(YSTEP, yfreq, 500000)
        
        sleep(xdelay * xdist)
        
        pi.hardware_PWM(XSTEP, xfreq, 0)
        pi.hardware_PWM(YSTEP, yfreq, 0)
        
        #Finish the rest of the Y distance to cover
        pi.hardware_PWM(YSTEP, yfreq, 500000)
        
        sleep(ydelay * (ydist - xdist))
    
        pi.hardware_PWM(YSTEP, yfreq, 0)
    
    if ydist < xdist:
        
        pi.hardware_PWM(XSTEP, xfreq, 500000)
        pi.hardware_PWM(YSTEP, yfreq, 500000)
        
        sleep(ydelay * ydist)
        
        pi.hardware_PWM(XSTEP, xfreq, 0)
        pi.hardware_PWM(YSTEP, yfreq, 0)
        
        #Finish the rest of the X distance to cover
        pi.hardware_PWM(XSTEP, xfreq, 500000)
        
        sleep(xdelay * (xdist - ydist))
    
        pi.hardware_PWM(XSTEP, xfreq, 0)
        
        
        
        
        
	
		


#Open file for reading coordinates and store them in X and Y arrays
x_coordinate = []
y_coordinate = []

with open('wave.txt', 'r') as user_file:
	reader = csv.reader(user_file, delimiter = ',')
	for row in reader:
		x_coordinate.append(row[0])
		y_coordinate.append(row[1])
		
#Get length of coordinate arrays
length = len(x_coordinate)

"""
Travel at .5mm increments
Go through each coordinate and based on ratio, give it number of pulses
Update x and y positions at each iteration
"""

#Movement is only going from 0 to max coordinate
while c < length:
	next_x = x_coordinate[c]
	next_y = y_coordinate[c]
	
	#Convert to ints
	next_x = int(next_x)
	next_y = int(next_y)
	
	print'Current Position: (%d, %d)' % (current_x, current_y)
	print'Next Position: (%d, %d)' % (next_x, next_y)
	
	#Function Call
	gotoXY(current_x, current_y, next_x, next_y)
	
	xpos = next_x
	ypos = next_y
	
	c = c + 1

print 'Number of Forward X pulses: ', xPulses
print 'Number of Forward Y pulses: ', yPulses
print'Final Forward Position: (%d, %d)' % (xpos, ypos)

#Subtract 1 from c to put the index back in range
c = c - 1


#Reverse the movement
while c > -1:
	
	next_x = x_coordinate[c]
	next_y = y_coordinate[c]
	
	#Convert to ints
	next_x = int(next_x)
	next_y = int(next_y)
	
	print'Current Position: (%d, %d)' % (xpos, ypos)
	print'Next Position: (%d, %d)' % (next_x, next_y)
	
	#Function Call
	gotoXY(current_x, current_y, next_x, next_y)
	
	xpos = next_x
	ypos = next_y
	
	c = c - 1

	
print 'Total Number of X pulses: ', totalX
print 'Total Number of Y pulses: ', totalY
print'Final Position: (%f, %f)' % (current_x, current_y)
	
	
		
		

