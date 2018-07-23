#!/usr/bin/env python
import keyboard
import RPi.GPIO as GPIO
import pigpio
from time import *



class Gantry():
	
	def __init__(self):
		"""
		All pins used by the Gantry will go here
		Pin Definitions:
		
		XDIR is the pin that sends pulses to the driver controlling the
		direction of the X axis motor
		YDIR is the pin that sends pulses to the driver controlling the
		direction of the Y axis motor
		
		XSTEP is the pin that sends pulses to the driver controlling the X
		axis motor to make it move
		YSTEP is the pin that sends pulses to the driver controlling the Y 
		axis motor to make it move 
		
		readX is the pin that reads the XSTEP pin to keep track of the
		number of pulses being sent
		readY is the pin that reads the YSTEP pin to keep track of the 
		number of pulses being sent
		
		These values should not change at all unless if something is changed
		on the circuit
		"""
		
		self.XDIR = 20
		self.XSTEP = 12
		self.YDIR = 19
		self.YSTEP = 13
		self.readX = 24
		self.readY = 21
		self.TTLPIN = 17
		
		"""
		These variables will hold the directions 
		CW = Clockwise
		CCW = Counter Clockwise
		"""
		self.CW = 1
		self.CCW = 0
		
		"""
		These variables will keep track of the current position of the Gantry
		They default to 0 each time an instance of this class is declared
		"""
		
		self.currentX = 0.
		self.currentY = 0.
		
		"""
		This list will represent the current position in an XY manner
		It will also be updated and returned in the getPos function
		"""
		
		self.currentPos = [self.currentX, self.currentY]
		
		
		"""
		This variable will keep track of the user defined speed
		Speed will be a multiplier that you multiply the delay by
		The speed will be set using the getSpeed function from within the class
		The variable speed will default to 1
		"""
		
		self.speed = 1
		
		"""
		This variable will be modified based on the TTL Pulse received
		"""
		self.TTL = 0
		
		"""
		These variables will be used to hold the locations of the head and tails of the fish
		"""
		self.xHead = 0.
		self.xTail = 0.
		self.yHead = 0.
		self.yTail = 0.
		
		"""
		These variables will store the current direction of the X and Y motors
		They will both default to Clockwise
		"""
		self.xdir = 1
		self.ydir = 1
		
		"""
		This variable will store the resolution of the motors
		They will default to 64 steps per full revolution which requires 12800 pulses
		according to the manual tha can be found at https://github.com/JorgeG30/gantry_control
		The resolution can be changed through the physical motors but any changes made
		to the configuration must be changed in the code as well via the GUI since it would
		throw off measurements
		"""
		self.xresolution = 64
		self.yresolution = 64
		
		
		"""
		These variables will store the number of pulses sent to both the X and Y motors
		Based on theses values, the current XY position of the motor is calculated
		They both start at 0
		"""
		self.xPulses = 0
		self.yPulses = 0
		
		"""
		Create resetable pulse counters to be used in path reading code
		"""
		self.xPulseReset = 0
		self.yPulseReset = 0
	
	"""
	This function updates the current position of the gantry based on the number of pulses sent
	This should be called everytime a pulse is sent either in the positive of negative direction
	"""
	def getPos(self):
		self.currentX = float(self.xPulses) / float(92)
		self.currentY = float(self.yPulses) / float(119)
		#print 'Current Position: (%f, %f)' % (self.currentX, self.currentY)
		
	"""
	These functions will be called in order to update xPulses and yPulses
	They will serve as the callback functions for the pulses sent
	"""
	
	def xPulseCount(self, channel):
		self.xPulseReset += 1
		if self.xdir == 0:
			self.xPulses -= 1
		elif self.xdir == 1:
			self.xPulses += 1
		self.getPos()
	
	def yPulseCount(self, channel):
		self.yPulseReset += 1
		if self.ydir == 0:
			self.yPulses -= 1
		elif self.ydir == 1:
			self.yPulses += 1
		self.getPos()
		
	"""
	This function is the callback that will receive the TTL pulse 
	from neural data collection hardware
	"""
	
	def TTLPulse(self, channel):
		self.TTL = 1
	
	
	"""
	These functions will be used to set the direction of the motor
	They will take in the difference in between the current coordinate 
	and the next coordinate
	"""
	
	def getxdir(self, distance):
		if distance < 0:
			self.xdir = 0
		elif distance > 0:
			self.xdir = 1
	
	def getydir(self, distance):
		if distance < 0:
			self.ydir = 0
		elif distance > 0:
			self.ydir = 1
	"""
	def keyboard_control(self):
		while True:
			
			self.getPos()
			
			if keyboard.is_pressed('d'):
				self.xdir = self.CW
				pi.write(self.XDIR, self.xdir)
				pi.write(self.XSTEP, 1)
				sleep(.0001)
				pi.write(self.XSTEP, 0)
				sleep(.0001)
				 
			if keyboard.is_pressed('a') and self.currentX != 0:
				self.xdir = self.CCW
				pi.write(self.XDIR, self.xdir)
				pi.write(self.XSTEP, 1)
				sleep(.0001)
				pi.write(self.XSTEP, 0)
				sleep(.0001)
				
			if keyboard.is_pressed('s') and self.currentY != 0 :
				self.ydir = self.CCW
				pi.write(self.YDIR, self.ydir)
				pi.write(self.YSTEP, 1)
				sleep(.0001)
				pi.write(self.YSTEP, 0)
				sleep(.0001)
				
			if keyboard.is_pressed('w'):
				self.ydir = self.CW
				pi.write(self.YDIR, self.ydir)
				pi.write(self.YSTEP, 1)
				sleep(.0001)
				pi.write(self.YSTEP, 0)
				sleep(.0001)
				
			if keyboard.is_pressed('esc'):
				break
			
			
		
		
	"""
	
	
		
		
		
	
	
