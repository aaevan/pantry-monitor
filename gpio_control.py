import RPi.GPIO as GPIO
from time import sleep
from random import randint, random
from read_scale import *

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
output_pins = (8, 10, 12, 16, 18)
#output_pins = (8,)
input_pins = (29, 31, 33, 35, 37)
#input_pins = (18,)
for pin in output_pins:
    print("output_pin: {}".format(pin))
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
for pin in input_pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

#GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW)
#GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def dummy_scale_output():
    """
    pretends to receive input from the USB scale.
    """
    for i in range(5):
        print("Weighing staple{}".format('.' * i))
        sleep(.2)
    result = randint(1, 100)
    print("weight: {}".format(result))
    return result

def set_all_low():
    for pin in output_pins:
        GPIO.output(pin, GPIO.LOW)

def set_all_high():
    for pin in output_pins:
        GPIO.output(pin, GPIO.HIGH)

def flash_all(rate=.1, n=3):
    for _ in range(n):
        set_all_high()
        sleep(rate)
        set_all_low()
        sleep(rate)

def main():
    """
    if the scale is detected, run through a looping LED animation.
    given a button press, go into weighing mode
    storing the staple that is to be weighed by which button was pressed.
    """
    try:
        count = 0
        while True:
            count = (count + 1) % 10
            input_states = [GPIO.input(pin) for pin in input_pins]
            output_states = [(pin, randint(0, 1)) for pin in output_pins]
            scale_value = easy_measure()
            [GPIO.output(*pin_state) for pin_state in output_states]
            print("{}|{}|{}|{}".format(count, input_states, output_states, scale_value))
            sleep(.1)
    except KeyboardInterrupt:
        print("setting all pins low. Exiting.")
        set_all_low()

main()
