from Tkinter import *
import ntpath
import tkMessageBox
from tkFileDialog import *
import keyboard
import RPi.GPIO as GPIO
import pigpio
from time import *
import gantry_class
import csv

#Connect to pigpio daemon
pi = pigpio.pi()

#Create an instance of the Gantry Class
gantry = gantry_class.Gantry()

#Set the GPIO mode for RPi.GPIO
GPIO.setmode(GPIO.BCM)

#Set readX and readY as inputs
GPIO.setup(gantry.readX, GPIO.IN)
GPIO.setup(gantry.readY, GPIO.IN)
GPIO.setup(gantry.TTLinput, GPIO.IN)

#Create callbacks for these pins
GPIO.add_event_detect(gantry.readX, GPIO.RISING, callback=gantry.xPulseCount)
GPIO.add_event_detect(gantry.readY, GPIO.RISING, callback=gantry.yPulseCount)
GPIO.add_event_detect(gantry.TTLinput, GPIO.RISING, callback = gantry.TTLPulse)

#This variable will store all of the files selected by the user
filenames = None

#These variables will be updated with the current state of the arrow buttons
right_pressed = 0
up_pressed = 0
down_pressed = 0
left_pressed = 0

#Variable that will be checked to end keyboard control
end_key = 0

#Initialize abortNum and continue_var to 0
abortNum = 0
continue_var = 0
pause_var = 0

#Variables that will be checked to determine head and tail position
head_button_press = 0
tail_button_press = 0

#Arrays that will store the coordinates and reverse coordinates
x_coordinate = []
y_coordinate = []

#Array that will store the new scaled coordinates
x_scaled = {}
y_scaled = {}

#Parameters that can be set based on user input
trials_per_file = {}
x_scale_vars = {}
y_scale_vars = {}

#Arrays for modifiable buttons, labels, etc
fileLabels = {}
trialEntries = {}
trialLabels = {}
xScaleButtons = {}
yScaleButtons = {}

"""
These are utility functions like extracting filenames from path
"""
def path_leaf(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)

"""
These functions will be used to send keyboard commands via onscreen GUI buttons
"""
def sendUp():
	global up_pressed
	up_pressed = 1

def sendDown():
	global down_pressed
	down_pressed = 1

def sendLeft():
	global left_pressed
	left_pressed = 1

def sendRight():
	global right_pressed
	right_pressed = 1

def end_keyboard_control():
	global end_key
	end_key = 1
	
def recordHead():
	gantry.xHead = gantry.currentX
	gantry.yHead = gantry.currentY
	xhead_value.config(text = str(gantry.xHead), width = 20)
	yhead_value.config(text = str(gantry.yHead), width = 20)
	xhead_value.update()
	yhead_value.update()

def recordTail():
	gantry.xTail = gantry.currentX
	gantry.yTail = gantry.currentY
	xtail_value.config(text = str(gantry.xTail), width = 20)
	ytail_value.config(text = str(gantry.yTail), width = 20)
	xtail_value.update()
	ytail_value.update()

def pause_execution():
	global pause_var
	global continue_var
	continue_var = 0
	pause_var = 1

def continue_execution():
	global continue_var
	global pause_var
	pause_var = 0
	continue_var = 1
	
def abort():
	global abortNum
	global filenames
	abortNum = 1
	filenames = None
	pi.clear_bank_1((1 << gantry.XSTEP) | (1 << gantry.YSTEP))
	gantry.xPulseReset = 0
	gantry.yPulseReset = 0
	gantry.getPos()
	
def pathScaling(axis):
	global x_coordinate
	global y_coordinate
	global x_scaled
	global y_scaled
	currentx_temp = {}
	currenty_temp = {}
	
	i = 0 
	while i < len(x_coordinate):
		x_coordinate[i] = float(x_coordinate[i])
		y_coordinate[i] = float(y_coordinate[i])
		i += 1
	
	"""
	Scaling algorithm:
	1. Calculate the difference between the head and tail values
	2. Calculate the difference between the maximum and minimum value of the coordinates (x or y)
	3. Calculate the ratio of 1 by 2
	4. Multiply the ratio by the difference between the coordinate and the minimum value of coordinate
	5. Add the head value to 4
	"""
	
	if axis == 1:
		
		"""
		Implement x scaling
		Check whether or not scaling is possible
		If not possible, leave coordinates as is
		"""
		if gantry.xHead != gantry.xTail:
			length = len(x_coordinate)
			max_xcoordinate = max(x_coordinate)
			min_xcoordinate = min(x_coordinate)
			range_diff = gantry.xTail - gantry.xHead
			value_diff = max_xcoordinate - min_xcoordinate
			c = 0
			""" Loop through the coordinates"""
			while c < length :
				currentx_temp[c] = x_coordinate[c] - min_xcoordinate
				x_scaled[c]      = (((range_diff)/(value_diff))*currentx_temp[c]) + gantry.xHead
				c+=1
	
	if axis == 2:
		
		"""
		Implement y scaling
		Check whether or not scaling is possible
		If not possible, leave coordinates as is
		"""
		if gantry.yHead != gantry.yTail:
			length = len(y_coordinate)
			max_ycoordinate = max(y_coordinate)
			min_ycoordinate = min(y_coordinate)
			range_diff = gantry.yTail - gantry.yHead
			value_diff = max_ycoordinate - min_ycoordinate
			c = 0
			""" Loop through the coordinates"""
			while c < length :
				currenty_temp[c]= y_coordinate[c] - min_ycoordinate
				y_scaled[c]      = (((range_diff)/(value_diff))*currenty_temp[c]) + gantry.yHead
				c += 1
	
def pathMovement(file_index, reverse):
	
	#Declare any global variables
	global abortNum
	global pause_var
	global outputFile
	global x_scaled
	global y_scaled
	global x_coordinate
	global y_coordinate
	
	oldx = x_coordinate
	oldy = y_coordinate
	
	if int(x_scale_vars[file_index].get()) == 1:
		x_coordinate = (x_scaled)
		
	if int(y_scale_vars[file_index].get()) == 1:
		y_coordinate = tuple(y_scaled)
	
	if reverse == 1:
		x_coordinate.reverse()
		y_coordinate.reverse()
	
	
	
	
	
	
	
	#Open file for appending
	file_obj = open(outputFile, 'a')
	
	
	#Set abortNum to 0 at the beginning of each function call
	abortNum = 0
	
	#Update current position of the gantry
	gantry.getPos()
	
	#Get the length of the coordinates of the current path
	length = len(x_coordinate)
	
	print 'Length of coordinates: ', length
	
	#Check whether or not path scaling is turned on or off
	
	delay = .0002
	speed = 1
	
	# Number of pulses for 0.5 mm
	xfreq = 92
	yfreq = 119
	
	#Declare counter and loop through the coordinates
	c = 0
	
	#Loop throguh the coordinates
	while c < length:
		
		#Set current and next variables
		currX = gantry.currentX
		currY = gantry.currentY
		nextX = x_coordinate[c]
		nextY = y_coordinate[c]
		
		print 'Next Coordinate: (%f, %f)' % (nextX, nextY)
		
		nextX = int(float(nextX))
		nextY = int(float(nextY))
		
		#Calculate the distance between the points
		distX = nextX - currX
		distY = nextY - currY
		
		#Determine direction of gantry based on distance and write to gantry
		gantry.getxdir(distX)
		gantry.getydir(distY)
		pi.write(gantry.XDIR, gantry.xdir)
		pi.write(gantry.YDIR, gantry.ydir)
		
		#Number of required pulses to travel for each point
		x_req = abs(distX * xfreq)
		y_req = abs(distY * yfreq)
		
		print x_req
		print y_req
		
		if x_req != 0 and y_req != 0:
			
			print 'Entering main if'
			
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
			
			if denominator >= numerator:
				while gantry.xPulseReset < x_req and gantry.yPulseReset < y_req:
				
					for j in range(denominator):
						if j < numerator:
							pi.set_bank_1((1<<gantry.XSTEP) | (1<<gantry.YSTEP))
							sleep(delay * speed)
							pi.clear_bank_1((1<<gantry.XSTEP) | (1<<gantry.YSTEP))
							sleep(delay * speed)
							xlabel.config(text = str(gantry.currentX))
							ylabel.config(text = str(gantry.currentY))
							xlabel.update()
							ylabel.update()
							file_obj.write(str(gantry.currentX) + ',' + str(gantry.currentY) + ',' + str(time()) + '\n')
							
							
						else:
							pi.write(gantry.YSTEP, 1)
							sleep(delay * speed)
							pi.write(gantry.YSTEP, 0)
							sleep(delay * speed)
							xlabel.config(text = str(gantry.currentX))
							ylabel.config(text = str(gantry.currentY))
							xlabel.update()
							ylabel.update()
							file_obj.write(str(gantry.currentX) + ',' + str(gantry.currentY) + ',' + str(time()) + '\n')
							
						
						if gantry.xPulseReset == x_req or gantry.yPulseReset == y_req:
							break
							
						if abortNum == 1:
							print 'Aborting Movement'
							root.update() 
							root.update_idletasks()
							return 1
						
						while pause_var == 1:
							root.update() 
							root.update_idletasks()
							if continue_var == 1:
								break
			
			xlabel.config(text = str(gantry.currentX))
			ylabel.config(text = str(gantry.currentY))
			xlabel.update()
			ylabel.update()
			
			if denominator < numerator:
				while gantry.xPulseReset < x_req and gantry.yPulseReset < y_req:
			
					for j in range(numerator):
						if j < denominator:
							pi.set_bank_1((1<<gantry.XSTEP) | (1<<gantry.YSTEP))
							sleep(delay * speed)
							pi.clear_bank_1((1<<gantry.XSTEP) | (1<<gantry.YSTEP))
							sleep(delay * speed)
							xlabel.config(text = str(gantry.currentX))
							ylabel.config(text = str(gantry.currentY))
							xlabel.update()
							ylabel.update()
							file_obj.write(str(gantry.currentX) + ',' + str(gantry.currentY) + ',' + str(time()) + '\n')
							
						else:
							pi.write(gantry.XSTEP, 1)
							sleep(delay * speed)
							pi.write(gantry.XSTEP, 0)
							sleep(delay * speed)
							xlabel.config(text = str(gantry.currentX))
							ylabel.config(text = str(gantry.currentY))
							xlabel.update()
							ylabel.update()
							file_obj.write(str(gantry.currentX) + ',' + str(gantry.currentY) + ',' + str(time()) + '\n')
							
						
						if gantry.xPulseReset == x_req or gantry.yPulseReset == y_req:
							break
						
						if abortNum == 1:
							print 'Aborting Movement'
							root.update() 
							root.update_idletasks()
							return 1
						
						while pause_var == 1:
							root.update() 
							root.update_idletasks()
							if continue_var == 1:
								break
		
		xlabel.config(text = str(gantry.currentX))
		ylabel.config(text = str(gantry.currentY))
		xlabel.update()
		ylabel.update()
				
		if gantry.xPulseReset < x_req and gantry.yPulseReset == y_req:
			while gantry.xPulseReset < x_req:

				pi.write(gantry.XSTEP, 1)
				sleep(delay * speed)
				pi.write(gantry.XSTEP, 0)
				sleep(delay * speed)
				xlabel.config(text = str(gantry.currentX))
				ylabel.config(text = str(gantry.currentY))
				xlabel.update()
				ylabel.update()
				file_obj.write(str(gantry.currentX) + ',' + str(gantry.currentY) + ',' + str(time()) + '\n')
				
				if abortNum == 1:
					print 'Aborting Movement'
					root.update() 
					root.update_idletasks()
					return 1
				
				while pause_var == 1:
					root.update() 
					root.update_idletasks()
					if continue_var == 1:
						break
		
		xlabel.config(text = str(gantry.currentX))
		ylabel.config(text = str(gantry.currentY))
		xlabel.update()
		ylabel.update()
				
		if gantry.yPulseReset < y_req and gantry.xPulseReset == x_req:	
			while gantry.yPulseReset < y_req:

				pi.write(gantry.YSTEP, 1)
				sleep(delay * speed)
				pi.write(gantry.YSTEP, 0)
				sleep(delay * speed)
				xlabel.config(text = str(gantry.currentX))
				ylabel.config(text = str(gantry.currentY))
				xlabel.update()
				ylabel.update()
				file_obj.write(str(gantry.currentX) + ',' + str(gantry.currentY) + ',' + str(time()) + '\n')
				
				if abortNum == 1:
					print 'Aborting Movement'
					root.update() 
					root.update_idletasks()
					return 1
					
				while pause_var == 1:
					root.update() 
					root.update_idletasks()
					if continue_var == 1:
						break
						
		xlabel.config(text = str(gantry.currentX))
		ylabel.config(text = str(gantry.currentY))
		xlabel.update()
		ylabel.update()
		
		#Increment Counter
		c += 1
		
		#Reset Pulse Counters for next coordinate use
		gantry.xPulseReset = 0
		gantry.yPulseReset = 0
	x_coordinate = oldx
	y_coordinate = oldy
		
		
		
	
	
	
	
	
	
	

def keyboard_control():
	global right_pressed
	global up_pressed
	global down_pressed
	global left_pressed
	global end_key
	global head_key
	global tail_key
	
	"""
	Initialize the press variables to 0 each time keyboard control is called
	"""
	right_pressed = 0
	up_pressed = 0
	down_pressed = 0
	left_pressed = 0
	
	"""
	These variables will be used to determine whether the head or tail of the 
	fish is being collected. The head must be collected first if doing it via keyboard.
	If collecting via onscreen GUI buttons, then either one can be collected first
	"""
	head = False
	tail = False
	
	while True:
			
			xlabel.config(text = str(gantry.currentX))
			ylabel.config(text = str(gantry.currentY))
			xlabel.update()
			ylabel.update()
			
			
			if keyboard.is_pressed('d') or right_pressed == 1:
				gantry.xdir = gantry.CW
				pi.write(gantry.XDIR, gantry.xdir)
				pi.write(gantry.XSTEP, 1)
				#sleep(.0001)
				pi.write(gantry.XSTEP, 0)
				#sleep(.0001)
				 
			if (keyboard.is_pressed('a') or left_pressed == 1) and gantry.currentX != 0:
				gantry.xdir = gantry.CCW
				pi.write(gantry.XDIR, gantry.xdir)
				pi.write(gantry.XSTEP, 1)
				#sleep(.0001)
				pi.write(gantry.XSTEP, 0)
				#sleep(.0001)
				
			if (keyboard.is_pressed('s') or down_pressed == 1) and gantry.currentY != 0 :
				gantry.ydir = gantry.CCW
				pi.write(gantry.YDIR, gantry.ydir)
				pi.write(gantry.YSTEP, 1)
				#sleep(.0001)
				pi.write(gantry.YSTEP, 0)
				#sleep(.0001)
				
			if keyboard.is_pressed('w') or up_pressed == 1:
				gantry.ydir = gantry.CW
				pi.write(gantry.YDIR, gantry.ydir)
				pi.write(gantry.YSTEP, 1)
				#sleep(.0001)
				pi.write(gantry.YSTEP, 0)
				#sleep(.0001)
				
			if keyboard.is_pressed('esc') or end_key == 1:
				break
				
			right_pressed = 0
			up_pressed = 0
			down_pressed = 0
			left_pressed = 0
	xlabel.config(text = str(gantry.currentX))
	ylabel.config(text = str(gantry.currentY))
	xlabel.update()
	ylabel.update()
	end_key = 0

def select_files():
	global filenames
	filenames = askopenfilenames(parent = root, title = 'Choose files')
	displayFiles()
	createScaleButtons()
	createTrialEntries()
	bindEntryLabels()

def displayFiles():
	global fileLabels
	global filenames
	global trialLabels
	global trials_per_file
	
	"""
	Check length of file labels. Destroy any previous labels and then create new ones
	"""
	j = 0
	labels_len = len(fileLabels)
	while j < labels_len:
		fileLabels[j].destroy()
		trialLabels[j].destroy()
		j += 1 
	
	"""
	Using path_leaf function, display the filenames without the path directory
	"""
	num_of_files = len(filenames)
	c = 0
	while c < num_of_files:
		only_filename = path_leaf(filenames[c])
		trials_per_file[c] = 1
		tmp_label = Label(paths_widget_frame, text = str(only_filename))
		tmp_trial_label = Label(paths_widget_frame, text = str(trials_per_file[c]))
		trialLabels[c] = tmp_trial_label
		fileLabels[c] = tmp_label
		fileLabels[c].grid(row = c + 1, column = 0)
		trialLabels[c].grid(row = c + 1, column = 4)
		c += 1

def createScaleButtons():
	global xScaleButtons
	global yScaleButtons
	global x_scale_vars
	global y_scale_vars
	global filenames
	
	"""
	Check for previous buttons
	If there are any, destroy them
	"""
	
	buttons_len = len(xScaleButtons)
	j = 0
	while j < buttons_len:
		xScaleButtons[j].destroy()
		yScaleButtons[j].destroy()
		j += 1
	
	"""
	Create new check buttons along with master control button
	"""
	num_of_files = len(filenames)
	c = 0
	while c < num_of_files:
		xtmp_var = IntVar()
		ytmp_var = IntVar()
		x_scale_vars[c] = xtmp_var
		y_scale_vars[c] = ytmp_var
		xtmp_button = Checkbutton(paths_widget_frame, variable = x_scale_vars[c])
		ytmp_button = Checkbutton(paths_widget_frame, variable = y_scale_vars[c])
		xScaleButtons[c] = xtmp_button
		xScaleButtons[c].grid(row = c + 1, column = 1)
		yScaleButtons[c] = ytmp_button
		yScaleButtons[c].grid(row = c + 1, column = 2)
		c += 1

def createTrialEntries():
	global trials_per_file
	global trialEntries
	global filenames
	
	"""
	Check whether there are already existing entry boxes
	Destroy any existing ones and default the trial values to 1
	"""
	entries_len = len(trialEntries)
	j = 0
	while j < entries_len:
		trials_per_file[j] = 1
		trialEntries[j].destroy()
		j += 1
	
	"""
	Create entry boxes based on the number of files 
	"""
	num_of_files = len(filenames)
	c = 0
	while c < num_of_files:
		tmp_entry = Entry(paths_widget_frame, width = 5)
		trialEntries[c] = tmp_entry
		trialEntries[c].grid(row = c + 1, column = 3)
		c += 1

def bindEntryLabels():
	
	global trialEntries
	global trials_per_file
	global filenames
	"""
	Here we will bind the entry labels to the return key
	When pressed, the trial label beside it will update 
	It will also store the value within the trials list
	"""
	
	entries_len = len(filenames)
	c = 0
	while c < entries_len:
		trialEntries[c].bind("<Return>", lambda event, index = c: updateTrials(event, index))
		c += 1
		
def updateTrials(event, index):
	global trialLabels
	global trialEntries
	global trials_per_file
	trials_per_file[index] = trialEntries[index].get()
	trialLabels[index].config(text = str(trials_per_file[index]))
	trialLabels[index].update()
	root.focus() 
	
	
def execute_files():
	
	global trials_per_file
	global abortNum
	global outputFile
	global x_scale_vars
	global y_scale_vars
	
	"""
	Check whether or not files have been selected
	If yes continue
	If not, give error message and return 1
	"""
	if filenames == None:
		tkMessageBox.showerror("Error","No files selected, Please select files before trying to start movement")
		return 1
		
	
	print len(filenames)
	global x_coordinate
	global y_coordinate
	"""
	Get the length of the filenames tuple
	"""
	
	num_files = len(filenames)
	
	"""
	Read each file one by one, treating each one as its own separate trial
	"""
	c = 0
	while c < num_files:
		#Counter that will be to determine how many times a path will be executed
		trial_num = 0
		
		with open(filenames[c], 'r') as user_file:
			reader = csv.reader(user_file, delimiter = ',')
			for row in reader:
				x_coordinate.append(row[0])
				y_coordinate.append(row[1])
		"""
		File format should be:
		xpos,ypos,timestamp
		"""
		#Remove extension from filename 
		filename_without_path = path_leaf(filenames[c])
		filename_without_ext = filename_without_path.split(".")
		
		#Determine whether or not to scale 
		if int(x_scale_vars[c].get()) == 1:
			pathScaling(1)
		
		if int(y_scale_vars[c].get()) == 1:
			pathScaling(2)
		
		#Repeatedly call pathMovement depending on how many trials specified
		while trial_num < int(trials_per_file[c]):
			
			#Create output file name
			outputFile = filename_without_ext[0] + '_trial_' + str(trial_num + 1) + '.txt'
			#print outputFile
			"""
			if gantry.TTL == 0:
				while True:
					print 'Entered TTL Loop'
					root.update() 
					root.update_idletasks()
					if gantry.TTL == 1:
						break
			"""
			
			pathMovement(c, 0)
			if abortNum == 1:
				return 1
			pathMovement(c, 1)
			
			if abortNum == 1:
				return 1
			gantry.TTLPulse = 0
			pi.write(gantry.TTLoutput, 1)
			trial_num += 1
			
			#sleep(wait_time)
			
		
		#Reset coordinate arrays to 0
		x_coordinate = []
		y_coordinate = []
		
		#Increment Counter
		c += 1
			
			

	
	
	

# GUI	
# ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- ----- 

root = Tk()

"""
This section of the GUI will take care of the size and layout of the window
"""
root.geometry("1000x500")
root.title("Gantry Control GUI")
left = Frame(root, borderwidth = 2, relief="solid", width = 500, height = 500)
right = Frame(root, borderwidth = 2, relief="solid", width = 500, height = 500)
#right.pack_propagate(False)

left.pack(side = "left", expand = True, fill = "both")
right.pack(side = "right", expand = True, fill = "both")

file_buttons_box = Frame(right, borderwidth = 2, relief = "solid")
file_buttons_box.pack(expand = True, fill = "both")

paths_box = Frame(right, borderwidth = 2, relief = "solid")
paths_box.pack(expand = True, fill = "both")
paths_box.pack_propagate(False)

paths_box_canvas = Canvas(paths_box)
#paths_box_canvas.grid(row = 0, column = 0, sticky = "news")
paths_box_canvas.pack(expand = True, fill = "both")

paths_canvas_scroll = Scrollbar(paths_box_canvas, orient = "vertical", command = paths_box_canvas.yview)
paths_canvas_scroll.pack(side = "right", fill = "y")
paths_box_canvas.configure(yscrollcommand = paths_canvas_scroll.set)

paths_widget_frame = Frame(paths_box_canvas)
paths_box_canvas.create_window((0, 0), window = paths_widget_frame, anchor = 'nw')







parameters_box = Frame(right, borderwidth = 2, relief = "solid")
parameters_box.pack(expand = True, fill = "both")




"""
These are labels that acts as titles for checkbuttons, entries, etc.
"""
file_title_label = Label(paths_widget_frame, text = "File Name", padx = 5)
file_title_label.grid(row = 0, column = 0)

xscale_label = Label(paths_widget_frame, text = "Scale X Axis", padx = 5)
xscale_label.grid(row = 0, column = 1)

yscale_label = Label(paths_widget_frame, text = "Scale Y Axis", padx = 5)
yscale_label.grid(row = 0, column = 2)

enterTrials_label = Label(paths_widget_frame, text = "Enter No. of Trials", padx = 5)
enterTrials_label.grid(row = 0, column = 3)

numTrials_title = Label(paths_widget_frame, text = "No. of Trials", padx = 5)
numTrials_title.grid(row = 0, column = 4)

"""
This section of the GUI will take care of the labels that will be used 
"""
currentx_label = Label(left, fg = "dark green")
currentx_label.config(text = "Current X Position: ")
currentx_label.place(x = 90, y = 70)

currenty_label = Label(left, fg = "dark green")
currenty_label.config(text = "Current Y Position: ")
currenty_label.place(x = 90, y = 90)

xlabel = Label(left, fg = "dark green")
xlabel.config(text = str(gantry.currentX), width = 20)
xlabel.place(x = 210, y = 70)

ylabel = Label(left, fg = "dark green")
ylabel.config(text = str(gantry.currentY), width = 20)
ylabel.place(x = 210, y = 90)

#These are just the labels that tell you what each value is
xhead_label = Label(left, fg = "dark green")
xhead_label.config(text = 'Current X Head Coordinate:')
xhead_label.place(x = 34, y = 120)

yhead_label = Label(left, fg = "dark green")
yhead_label.config(text = 'Current Y Head Coordinate: ')
yhead_label.place(x = 34, y = 140)

xtail_label = Label(left, fg = "dark green")
xtail_label.config(text = 'Current X Tail Coordinate: ')
xtail_label.place(x = 46, y = 170)

ytail_label = Label(left, fg = "dark green")
ytail_label.config(text = 'Current Y Tail Coordinate: ')
ytail_label.place(x = 46, y = 190)

#These are the labels for the actual values
xhead_value = Label(left, fg = "dark green")
xhead_value.config(text = str(gantry.xHead), width = 20)
xhead_value.place(x = 210, y = 120)

yhead_value = Label(left, fg = "dark green")
yhead_value.config(text = str(gantry.yHead), width = 20)
yhead_value.place(x = 210, y = 140)

xtail_value = Label(left, fg = "dark green")
xtail_value.config(text = str(gantry.xTail), width = 20)
xtail_value.place(x = 210, y = 170)

ytail_value = Label(left, fg = "dark green")
ytail_value.config(text = str(gantry.yTail), width = 20)
ytail_value.place(x = 210, y = 190)

auto_control = Label(file_buttons_box, fg = "dark green", text = "Autonomous Control", width = 20)
auto_control.pack()

"""
This section takes care of the buttons that are used in the GUI
"""
keyboard_button = Button(left, text = 'Start Manual Control', width = 25, command = keyboard_control)
keyboard_button.pack()

selected_files = Button(file_buttons_box, text = 'Select Files to Open', width = 25, command = select_files)
selected_files.pack()

execute_files = Button(file_buttons_box, text = 'Start Movement', width = 25, command = execute_files)
execute_files.pack()

stop = Button(file_buttons_box, text = 'Pause Movement', width = 25, command = pause_execution)
stop.pack()

continue_butt = Button(file_buttons_box, text = 'Continue Movement', width = 25, command = continue_execution)
continue_butt.pack()

abort = Button(file_buttons_box, text = 'Abort', width = 25, command = abort)
abort.pack()

end_keyboard_button = Button(left, text = 'End Manual Control', width = 25, command = end_keyboard_control)
end_keyboard_button.pack()

up_button = Button(left, text = 'UP', width = 10, command = sendUp)
up_button.place(x = 170, y = 300)

down_button = Button(left, text = 'DOWN', width = 10, command = sendDown)
down_button.place(x = 170, y = 350)

left_button = Button(left, text = 'LEFT', width = 10, command = sendLeft)
left_button.place(x = 80, y = 325)

right_button = Button(left, text = 'RIGHT', width = 10, command = sendRight)
right_button.place(x = 260, y = 325)

head_button = Button(left, text = 'Record Head', width = 15, command = recordHead)
head_button.place(x = 145, y = 230)

tail_button = Button(left, text = 'Record Tail', width = 15, command = recordTail)
tail_button.place(x = 145, y = 260)

"""
These will be entries that should not be destroyed at all
Things like wait time between pulses or speed input
"""
#wait_time_entry = 


"""
This should be the end of the GUI
"""
root.mainloop()
