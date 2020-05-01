import numpy as np
import time
import math
import RPi.GPIO as GPIO
from progress.bar import PixelBar

class astrotracker:
    def __init__(self, radius, pins, exposure_time, Leds):
        self.radius = radius # mm
        print("Radius (mm) has been set equal to: ",self.radius)
        self.angular_velocity = 0.00007292115761437 # rad/sec
        print("Angular velocity (rad/sec) has been set equal to: ",self.angular_velocity)
        self.exposure_time = exposure_time  # exposure time of photograph in sec
        print("Exposure_time (sec) has been set equal to: ",self.exposure_time)
        self.thread_pitch=0.7 # mm
        print("Thread pitch (mm) has been set equal to: ",self.thread_pitch)
        #the total gear ratio taking into account the initial gear ratio of the stepper motor (28BYJ48)
        #and any other gears that are installed on the tracker
        self.gear_ratio = 63.68395*30./13.
        print("Gear ratio has been set equal to: ",self.gear_ratio)
        #delay for a faster speed
        self.delay_reset_position = 0.003
        
        #initialization of further variables
        self.delay = None #delay to control the speed of the tracker
        self.Pins = pins
        self.Leds= Leds
        self.Method = None # drive method of the stepper motor
        self.step_angle = None # angle per step according to drive method
        self.step_per_rev = None # steps per revolution according to drive method
        self.duration = None # duration of operation
        self.rps = self.angular_velocity*self.radius*self.gear_ratio/self.thread_pitch
        self.step_per_sec = None
        
        #set mode of the GPIO, BOARD or BCM
        GPIO.setmode(GPIO.BOARD)
        #setup and initialization of pins for stepper motor and installed Leds
        for p in self.Pins:
          GPIO.setup(p, GPIO.OUT)
          GPIO.output(p, 0)
        for l in self.Leds:
          GPIO.setup(l, GPIO.OUT)
          GPIO.output(l, 0)
        GPIO.output(12, True)

    # function to set the driving method    
    def set_mode(self,mode):
        if mode == 1:
          self.method = "Wave Drive"
          print ("Driving method:", self.method)
          self.sequence = [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]]
          self.step_angle = 11.25 #deg
          self.step_per_rev = 360. /self.step_angle
          self.step_per_sec = self.step_per_rev*self.rps
          self.delay = 1./self.step_per_sec
          print("delay is: ",self.delay)
          print("rps is: ",self.rps)
          print("steps per revolution are: ",self.step_per_rev)
        elif mode == 2:
          self.method = "Full Step"
          print("Driving method:", self.method)
          self.sequence = [
            [1, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 1],
            [1, 0, 0, 1]]
          self.step_angle = 11.25 #deg
          self.step_per_rev = 360. /self.step_angle
          self.step_per_sec = self.step_per_rev*self.rps
          self.delay = 1./self.step_per_sec
          print("delay is: ",self.delay)
          print("rps is: ",self.rps)
          print("steps per revolution are: ",self.step_per_rev)
        elif mode == 3:
          self.method = "Half Step"
          print("Driving method:", self.method)
          self.sequence = [
            [1, 0, 0, 0],
            [1, 1, 0, 0],
            [0, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 1, 0],
            [0, 0, 1, 1],
            [0, 0, 0, 1],
            [1, 0, 0, 1]]
          self.step_angle = 11.25/2. #deg
          self.step_per_rev = 360. /self.step_angle
          self.step_per_sec = self.step_per_rev*self.rps
          self.delay = 1./self.step_per_sec
          print("delay is: ",self.delay)
          print("rps is: ",self.rps)
          print("steps per revolution are: ",self.step_per_rev)
    #function to start the motion of the tracker
    def start_motion(self,error):
        GPIO.output(12, False)
        GPIO.output(16, True)
        self.set_mode(3)
        number_of_steps = int(math.ceil(self.exposure_time*self.step_per_sec))
        print("required steps are: ",number_of_steps)
        print("precalculated error is set to: ", error, "%")
        step = 0
        progress_bar= PixelBar('Progress bar', max=number_of_steps)
        start = time.time()
        while step<number_of_steps:
            for seq_step in range(len(self.sequence)):
                for pin in range(4):
                  GPIO.output(self.Pins[pin], self.sequence[seq_step][pin])
                time.sleep(self.delay-error/100.*self.delay)
                step = step + 1
                progress_bar.next()
                if(step >= number_of_steps):
                    break
        end = time.time()
        progress_bar.finish()
        self.duration = round(end-start,8)
        print("total steps counted were: ",step)
        print("duration measured was: ", self.duration)
        print("error (%): ",100.*round((self.exposure_time-self.duration)/self.exposure_time,8))
        GPIO.output(12, True)
        GPIO.output(16, False)
    
    #function to reset the tracker to initial position
    def reset_tracker(self):
        GPIO.output(12, False)
        GPIO.output(18, True)
        self.set_mode(2)
        start = time.time()
        step = 0
        number_of_steps = math.ceil(self.exposure_time*self.step_per_sec)
        progress_bar= PixelBar('Progress bar', max=number_of_steps)
        while step < number_of_steps:
          for seq_step in reversed(range(len(self.sequence))):
            step = step + 1
            for pin in range(4):
              GPIO.output(self.Pins[pin], self.sequence[seq_step][pin])
            time.sleep(self.delay_reset_position)
            progress_bar.next()
            if(step >= number_of_steps):
                break
        progress_bar.finish()
        GPIO.output(12, True)
        GPIO.output(18, False)
        
    #function to free the GPIOs    
    def clear(self):
        GPIO.output(12, False)
        GPIO.cleanup()
