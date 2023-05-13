import time
from gpiozero import Button
from signal import pause

def button_pressed():
    print("Ding dong ding dong")
    print("==========================")

def button_released():
    print("Stop")
    print("++++++++++++++++++++++++++")

button = Button(21)
button.when_pressed = button_pressed
button.when_released = button_released
pause()