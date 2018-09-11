# gantry_control
This Repository will contain files pertaining to the Gantry Control Project. 
The gantry is a multi axis linear robot that is controlled
by a Raspberry Pi 3 along with stepper motor drivers and an accompanying circuit.

Software Requirements:
Requires PIGPIO, RPi.GPIO, Tkinter

There are different codes in this repository. 
Each demonstrates a different function that is included in the main program.

keyboard_control.py: Allows control over the gantry using the keyboard connected to the Pi running the script. 
Up, down, left, right are mapped to W, S, A, D respectively.

pwm_keyboard_control.py: It is similar to keyboard_control.py but instead of sending
separate pulses to the GPIO pins, a dutycycle is turned on and off in order to send the pulses
to the stepper drivers

read_from_file.py: Allows autonomous movement of the gantry, with movement defined by coordinates in a text file.
The Pi will send pulses based on the coordinate specified in the file. Format of the file must be X,Y format with a
newline separating each coordinate

pwm_read_from_file.py: Similar to read_from_file.py, but instead of sending separate pulses, a dutycycle is turned on and off
in order to move the gantry.

gantry_class.py: Class that is used in gantry_gui.py that includes pin definitions, starting values, etc.

gantry_gui.py: Main program that brings previous codes together into one. Combines everything into one program and 
makes it user friendly with a GUI made using Tkinter

A circuit must be created in order to allow the stepper motor drivers to control the motors on the robot. The python scripts will
control the drivers by sending pulses to the drivers using the GPIO pins. Sending the pulses will make the motors on the robot move.


