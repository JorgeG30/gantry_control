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


#Define callback functions for pulses
def XPulse(gpio, level, tick):
	global xPulses
	global coordinate_based_xdir
	if coordinate_based_xdir == 0:
		xPulses = xPulses - 1
	elif coordinate_based_xdir == 1:
		xPulses = xPulses + 1
	
def YPulse(gpio, level, tick):
	global yPulses
	global coordinate_based_ydir
	if coordinate_based_ydir == 0:
		yPulses = yPulses - 1
	elif coordinate_based_ydir == 1:
		yPulses = yPulses + 1
	
def XPulseDist(gpio, level, tick):
	global xPulseCount
	xPulseCount = xPulseCount + 1
		
def YPulseDist(gpio, level, tick):
	global yPulseCount
	yPulseCount = yPulseCount + 1



#Create Callbacks
cb1 = pi.callback(readX, pigpio.RISING_EDGE, XPulse)
cb2 = pi.callback(readY, pigpio.RISING_EDGE, YPulse)
cb3 = pi.callback(readX, pigpio.RISING_EDGE, XPulseDist)
cb4 = pi.callback(readY, pigpio.RISING_EDGE, YPulseDist)

#Function for determining the direction of the motor
def determine_direction(dist):
	
	#Set direction to a default value
	direction = CW
	
	if dist > 0:
		direction = CW
	elif dist < 0:
		direction= CCW
	
	#Return direction
	return direction
		
	
#Functions for going to a certain X or Y
def gotoXY(currX, currY, nextX, nextY):
	# Number of pulses for 0.5 mm
	xfreq = 92 
	yfreq = 119
	
	# Traveling distance
	dist_X = nextX - currX
	dist_Y = nextY - currY
	
	#Call direction function and store within a variable
	global coordinate_based_xdir
	global coordinate_based_ydir
	coordinate_based_xdir = determine_direction(dist_X)
	coordinate_based_ydir = determine_direction(dist_Y)
	
	global xPulseCount
	global yPulseCount
	global xPulses
	global yPulses
	total_x = xPulses
	total_y = yPulses
	
	pi.write(XDIR, coordinate_based_xdir)
	pi.write(YDIR, coordinate_based_ydir)
	
	
	
	if dist_X != 0 and dist_Y != 0:
		while xPulseCount < abs(dist_X * xfreq) and yPulseCount < abs(dist_Y * yfreq):
				pi.set_bank_1((1<<XSTEP) | (1<<YSTEP))
				pi.clear_bank_1((1<<XSTEP) | (1<<YSTEP))
				current_x = float(xPulses)/float(xfreq)
				current_y = float(yPulses)/float(yfreq)
				print 'Current Position: (%f, %f)' % (current_x, current_y)
				
			
		while xPulseCount < abs(dist_X * xfreq):
				pi.write(XSTEP, 1)
				pi.write(XSTEP, 0)
				current_x = float(xPulses)/float(xfreq)
				current_y = float(yPulses)/float(yfreq)
				print 'Current Position: (%f, %f)' % (current_x, current_y)
				
		while yPulseCount < abs(dist_Y * yfreq):
				pi.write(YSTEP, 1)
				pi.write(YSTEP, 0)
				current_x = float(xPulses)/float(xfreq)
				current_y = float(yPulses)/float(yfreq)
				print 'Current Position: (%f, %f)' % (current_x, current_y)
				
	# Reset Pulse counters once the new point has been reached
	xPulseCount = 0
	yPulseCount = 0
		
#Define current position of X and Y
xpos = 0
ypos = 0

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
Travel at 1mm increments
Go through each coordinate and based on ratio, give it number of pulses
Update x and y positions at each iteration
"""
#Counter 
c = 0

#Movement is only going from 0 to max coordinate
while c < length:
	next_x = x_coordinate[c]
	next_y = y_coordinate[c]
	
	#Convert to ints
	next_x = int(next_x)
	next_y = int(next_y)
	
	print'Current Position: (%d, %d)' % (xpos, ypos)
	print'Next Position: (%d, %d)' % (next_x, next_y)
	
	#Function Call
	gotoXY(xpos, ypos, next_x, next_y)
	
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
	gotoXY(xpos, ypos, next_x, next_y)
	
	xpos = next_x
	ypos = next_y
	
	c = c - 1
	
	
print 'Number of X pulses: ', xPulses
print 'Number of Y pulses: ', yPulses
print'Final Position: (%d, %d)' % (xpos, ypos)
	
	
		
		
