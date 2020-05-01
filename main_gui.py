import Astrotracker
from Tkinter import *
import RPi.GPIO as GPIO

try:
    # set the pins in Raspberry board, mode: BOARD
    pins=[7, 11, 13, 15]
    Led_pins = [12,16,18]
    print("Pins and led Pins of raspberry are set. \nTo edit, check the source code: lines 6 and 7 \n")
    print("Provide information about exposure time, radius, time error and then press setup")
    print("The Red Led will turn on")
    print("\nError is about the error between the given exposure time and the measured time")
    print("Error = (exposure_time - measured_time)/exposure_time")
    print("\nChoose a function from the radiobuttons and press start")
    print("Green light will be on for motion function, Yellow Led for reset")
    print("\nCtrl+C ends the program\n")

    # gui setup
    root = Tk()
    root.title("Astrotracker");

    # default values
    def_shutter_speed = IntVar()
    def_shutter_speed.set(30)
    def_radius = IntVar()
    def_radius.set(200)
    def_error = IntVar()
    def_error.set(10.53486)

    Label(root, text= "Provide information about exposure time, radius, error and press setup.").grid(row=0, columnspan=2)
    Label(root, text= "Exposure time (seconds) :").grid(row=1)
    Label(root, text= "Radius (mm) : ").grid(row=2)
    Label(root, text= "Time Error (%) : ").grid(row=3)

    s = Entry(root, bd=1, text = def_shutter_speed)
    s.grid(row=1, column=1)
    r = Entry(root, bd=1, text = def_radius)
    r.grid(row=2, column=1)
    e = Entry(root, bd=1, text = def_error)
    e.grid(row=3, column=1)


    # setup method for button setup
    def setup():
        global nikon
        global radius
        global error
        exposure_time = int(s.get())
        radius = int(r.get())
        error = float(e.get())
        nikon = Astrotracker.astrotracker(radius,pins,exposure_time,Led_pins)
        print("\nRed light is On, succesful setup of tracker")
    Button(root, text="Setup", command=setup).grid(row=4)

    # Radiobutton
    var = IntVar()

    R1 = Radiobutton(root, text="start the tracker, anticlockwise motion", variable=var, value=1)
    R1.grid(row=5,column=0,sticky="W")

    R2 = Radiobutton(root, text="reset the tracker, clockwise motion", variable=var, value=2)
    R2.grid(row=6,column=0,sticky="W")

    R3 = Radiobutton(root, text="clear GPIOs", variable=var, value=3)
    R3.grid(row=7,column=0,sticky="W")
    
    # Motion method for Radiobuttons
    def Motion():
        e = var.get()
        if e==1:
            print("\nGreen LED is on, star tracking started")
            nikon.start_motion(error)
        elif e==2:
            print("\nYellow LED is on, reset started")
            nikon.reset_tracker()
        elif e==3:
            nikon.clear()
            print("\nGPIOs are cleared")

    Button(root, text="Start", command=Motion).grid(row=8,column=0)

    def close_tracker():
        GPIO.cleanup()
        root.quit()
        
    Button(root, text='Close', command=close_tracker).grid(row=8, column=1)
    root.mainloop()
except KeyboardInterrupt:
    GPIO.cleanup()
