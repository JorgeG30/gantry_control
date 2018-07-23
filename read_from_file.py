"""
	This code will use PIGPIO to send pulses and RPi.GPIO to read the state of GPIOs
	and update a pulse counter
""" 
from time import *
import pigpio
import keyboard
import rotary_encoder
import csv
import RPi.GPIO as GPIO
from decimal import *

#Connect to pigpio daemon
pi = pigpio.pi()

#Set GPIO mode
GPIO.setmode(GPIO.BCM)

#Define the Pins being used
XDIR = 20
XSTEP = 12
YDIR = 19
YSTEP = 13
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

#Set readX and readY as inputs
GPIO.setup(readX, GPIO.IN)
GPIO.setup(readY, GPIO.IN)

#Create callbacks for readX and readY
def XPulse(channel):
	global xPulses
	global countX
	global xdir
	global xPulseCount
	if xdir == 0:
		xPulses = xPulses - 1
	elif xdir == 1:
		xPulses = xPulses + 1
	xPulseCount = xPulseCount + 1

def YPulse(channel):
	global yPulses
	global ydir
	global yPulseCount
	if ydir == 0:
		yPulses = yPulses - 1
	elif ydir == 1:
		yPulses = yPulses + 1
	yPulseCount = yPulseCount + 1

#Add event detection to readX and readY
GPIO.add_event_detect(readX, GPIO.RISING, callback=XPulse)
GPIO.add_event_detect(readY, GPIO.RISING, callback=YPulse)  

#Default xdir and ydir to 1
xdir = 1
ydir = 1

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
	global xdir
	global ydir
	global current_x
	global current_y
	xdir = determine_direction(dist_X)
	ydir = determine_direction(dist_Y)
	
	global xPulseCount
	global yPulseCount
	global xPulses
	global yPulses
	total_x = xPulses
	total_y = yPulses
	
	pi.write(XDIR, xdir)
	pi.write(YDIR, ydir)
	
	delay = .0001
	speed = 1
	
	#Number of required pulses to travel for each point
	x_req = abs(dist_X * xfreq)
	y_req = abs(dist_Y * yfreq)
	
	print 'Required X Pulses: ', x_req
	print 'Required Y Pulses: ', y_req
	
	#sleep(2)
	
	if x_req != 0 and y_req != 0:
		
		#Set up ratio to determine number of pulses required to send 
		ratio = float(x_req)/float(y_req)
		
		#Check the numerator
		if ratio < .05:
			numerator = ratio * (10 ** 3)
			denominator = 10 ** 3
			numerator = round(numerator)
		elif ratio >= .05 and ratio < 10:
			numerator = float(ratio)*float(10)
			denominator = 10
			numerator = int(round(numerator))
		
		else:
			numerator = int(round(ratio))
			denominator = 1 
			
		print 'Numerator: ', numerator
		print 'Denominator: ', denominator
		
		if denominator >= numerator:
			while xPulseCount < x_req and yPulseCount < y_req:
				print 'Entering first while loop'
				for j in range(denominator):
					if j < numerator:
						pi.set_bank_1((1<<XSTEP) | (1<<YSTEP))
						sleep(delay * speed)
						pi.clear_bank_1((1<<XSTEP) | (1<<YSTEP))
						sleep(delay * speed)
						current_x = float(xPulses) / float(xfreq)
						current_y = float(yPulses) / float(yfreq)
						print 'Current Position: (%f, %f)' % (current_x, current_y)
						print ''
					else:
						pi.write(YSTEP, 1)
						sleep(delay * speed)
						pi.write(YSTEP, 0)
						sleep(delay * speed)
						current_x = float(xPulses) / float(xfreq)
						current_y = float(yPulses) / float(yfreq)
						print 'Current Position: (%f, %f)' % (current_x, current_y)
						print ''
					
					if xPulseCount == x_req or yPulseCount == y_req:
						break
		if denominator < numerator:
			while xPulseCount < x_req and yPulseCount < y_req:
				print 'Entering first while loop'
				for j in range(numerator):
					if j < denominator:
						pi.set_bank_1((1<<XSTEP) | (1<<YSTEP))
						sleep(delay * speed)
						pi.clear_bank_1((1<<XSTEP) | (1<<YSTEP))
						sleep(delay * speed)
						current_x = float(xPulses) / float(xfreq)
						current_y = float(yPulses) / float(yfreq)
						print 'Current Position: (%f, %f)' % (current_x, current_y)
						print ''
					else:
						pi.write(XSTEP, 1)
						sleep(delay * speed)
						pi.write(XSTEP, 0)
						sleep(delay * speed)
						current_x = float(xPulses) / float(xfreq)
						current_y = float(yPulses) / float(yfreq)
						print 'Current Position: (%f, %f)' % (current_x, current_y)
						print ''
					
					if xPulseCount == x_req or yPulseCount == y_req:
						break
			
	if xPulseCount < x_req and yPulseCount == y_req:
		while xPulseCount < x_req:
			print 'Entering X while loop'
			pi.write(XSTEP, 1)
			sleep(delay * speed)
			pi.write(XSTEP, 0)
			sleep(delay * speed)
			#print 'Number of X Pulses: %f' % xPulses
			#print 'Number of Y Pulses: %f' % yPulses
			"""
			pi.hardware_PWM(XSTEP, 8*xfreq , 500000)
			sleep(.125)
			pi.hardware_PWM(XSTEP, xfreq , 0)
			"""
			current_x = float(xPulses)/float(xfreq)
			current_y = float(yPulses)/float(yfreq)
			print 'Current Position: (%f, %f)' % (current_x, current_y)
			print ''
	
	if yPulseCount < y_req and xPulseCount == x_req:	
		while yPulseCount < y_req:
			print 'Entering Y while loop'
			pi.write(YSTEP, 1)
			sleep(delay * speed)
			pi.write(YSTEP, 0)
			sleep(delay * speed)
			#print 'Number of X Pulses: %f' % xPulses
			#print 'Number of Y Pulses: %f' % yPulses
			"""
			pi.hardware_PWM(YSTEP, 8*yfreq , 500000)
			sleep(.125)
			pi.hardware_PWM(YSTEP, yfreq , 0);
			"""
			current_x = float(xPulses)/float(xfreq)
			current_y = float(yPulses)/float(yfreq)
			print 'Current Position: (%f, %f)' % (current_x, current_y)
			print ''
		
		
	
	"""
	#Check the number of pulses sent, if gone above then go backwards
	extra_xpulses = abs(xPulseCount - x_req)
	extra_ypulses = abs(yPulseCount - y_req)
	
	#Position before entering loop
	
	
	if extra_xpulses > 0:
		sleep(.1)	
		if xdir == CW:
			xdir = CCW
			pi.write(XDIR, xdir)
			c = 0
			current_x = float(xPulses)/float(xfreq)
			current_y = float(yPulses)/float(yfreq)
			print 'Position before entering X loop: (%f, %f)' % (current_x, current_y)
			print 'Entering extra X while loop'
			while c < extra_xpulses:
				pi.write(XSTEP, 1)
				sleep(delay * speed)
				pi.write(XSTEP, 0)
				sleep(delay * speed)
				current_x = float(xPulses)/float(xfreq)
				current_y = float(yPulses)/float(yfreq)
				print 'Current Position: (%f, %f)' % (current_x, current_y)
				print ''
				c += 1
			print 'Exiting extra X while loop'
			print ''
		elif xdir == CCW:
			xdir = CW
			pi.write(XDIR, xdir)
			c = 0
			print 'Entering extra X while loop'
			while c < extra_xpulses:
				pi.write(XSTEP, 1)
				sleep(delay * speed)
				pi.write(XSTEP, 0)
				sleep(delay * speed)
				current_x = float(xPulses)/float(xfreq)
				current_y = float(yPulses)/float(yfreq)
				print 'Current Position: (%f, %f)' % (current_x, current_y)
				print ''
				c += 1
			print 'Exiting extra X while loop'
			current_x = float(xPulses)/float(xfreq)
			current_y = float(yPulses)/float(yfreq)
			print 'Position after exiting X loop: (%f, %f)' % (current_x, current_y)
			print ''
	sleep(.1)
	
	
	
	if extra_ypulses > 0:
		sleep(.1)	
		if ydir == CW:
			ydir = CCW
			pi.write(YDIR, ydir)
			j = 0
			current_x = float(xPulses)/float(xfreq)
			current_y = float(yPulses)/float(yfreq)
			print 'Position before entering Y loop: (%f, %f)' % (current_x, current_y)
			print 'Entering extra Y while loop'
			while j < extra_ypulses:
				pi.write(YSTEP, 1)
				sleep(delay * speed)
				pi.write(YSTEP, 0)
				sleep(delay * speed)
				current_x = float(xPulses)/float(xfreq)
				current_y = float(yPulses)/float(yfreq)
				print 'Current Position: (%f, %f)' % (current_x, current_y)
				print ''
				j += 1
			print 'Exiting extra Y while loop'
		elif ydir == CCW:
			ydir = CW
			pi.write(YDIR, ydir)
			j = 0
			print 'Entering extra Y while loop'
			while j < extra_ypulses:
				pi.write(YSTEP, 1)
				sleep(delay * speed)
				pi.write(YSTEP, 0)
				sleep(delay * speed)
				current_x = float(xPulses)/float(xfreq)
				current_y = float(yPulses)/float(yfreq)
				print 'Current Position: (%f, %f)' % (current_x, current_y)
				print ''
				j += 1
			print 'Exiting extra Y while loop'
			current_x = float(xPulses)/float(xfreq)
			current_y = float(yPulses)/float(yfreq)
			print 'Position after exiting Y loop: (%f, %f)' % (current_x, current_y)
			print ''
	"""
	# Reset Pulse counters once the new point has been reached
	xPulseCount = 0
	yPulseCount = 0
		
#Define current position of X and Y
xpos = 0
ypos = 0

#Open file for reading coordinates and store them in X and Y arrays
x_coordinate = []
y_coordinate = []

with open('square.txt', 'r') as user_file:
	reader = csv.reader(user_file, delimiter = ',')
	for row in reader:
		x_coordinate.append(row[0])
		y_coordinate.append(row[1])
		
#Get length of coordinate arrays
length = len(x_coordinate)
"""
#This part is unnecessary
#Calculate the total number of pulses required to get through each point in the file
i = length - 1
num_xpulses = int(x_coordinate[i])*92
num_ypulses = int(y_coordinate[i])*119
num_xpulses = num_xpulses * 2
num_ypulses = num_ypulses * 2
"""
"""
Travel at 1mm increments
Go through each coordinate and based on ratio, give it number of pulses
Update x and y positions at each iteration
"""
#Counter 
c = 0
current_x = 0
current_y = 0

#Movement is only going from 0 to max coordinate
while c < length:
	next_x = x_coordinate[c]
	next_y = y_coordinate[c]
	
	#Convert to ints
	next_x = float(next_x)
	next_y = float(next_y)
	
	#Function Call
	gotoXY(current_x, current_y, next_x, next_y)
	
	current_x = float(xPulses)/float(92)
	current_y = float(yPulses)/float(119)
	
	print'Current Position in main: (%f, %f)' % (current_x, current_y)
	#print'Next Position in main: (%f, %f)' % (next_x, next_y)
	
	xpos = next_x
	ypos = next_y
	
	#sleep(.1)
	
	c = c + 1

print 'Number of Forward X pulses: ', xPulses
print 'Number of Forward Y pulses: ', yPulses
print'Final Forward Position: (%f, %f)' % (xpos, ypos)

#Subtract 1 from c to put the index back in range
c = c - 1

#Reverse the movement
while c > -1:
	
	next_x = x_coordinate[c]
	next_y = y_coordinate[c]
	
	#Convert to ints
	next_x = float(next_x)
	next_y = float(next_y)
	
	#Function Call
	gotoXY(current_x, current_y, next_x, next_y)
	
	current_x = float(xPulses)/float(92)
	current_y = float(yPulses)/float(119)
	
	print'Current Position in main: (%f, %f)' % (current_x, current_y)
	print'Next Position in main: (%f, %f)' % (next_x, next_y)
	
	c = c - 1

print 'Remaining X Pulses: ', xPulses
print 'Remaining Y Pulses: ', yPulses

print 'Number of X Pulses required to reach the last point: ', num_xpulses
print 'Number of Y Pulses required to reach the last point: ', num_ypulses 

current_x = float(xPulses) / float(92)
current_y = float(yPulses) / float(119)

print'Final Position: (%f, %f)' % (current_x, current_y)
