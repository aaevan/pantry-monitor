import RPi.GPIO as GPIO
from time import sleep
from random import randint, random
from read_scale import *
from itertools import cycle

staples = ('black beans', 'brown rice', 'flour', 'kosher salt', 'MSG')

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
output_pins = (8, 10, 12, 16, 18)
input_pins = (29, 31, 33, 35, 37)
runner = cycle(output_pins)
flipper = cycle((GPIO.HIGH, GPIO.LOW))

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
        choice_timeout = 0
        staple_choice = None
        choice_pin = None
        last_measure = 0.0
        scale_value = 0.0
        measurement_repeats = 0
        while True:
            count = (count + 1) % 10
            input_states = [GPIO.input(pin) for pin in input_pins]
            last_measure = scale_value
            scale_value = easy_measure()
            #Track how many repeated measurements
            if scale_value == last_measure and scale_value != (0.0, 'g'):
                measurement_repeats += 1
            elif scale_value != last_measure and staple_choice is not None:
                choice_timeout += 2
            else:
                measurement_repeats = 0
            if scale_value is not None:
                output_string = "count:{}|input_states:{}|scale_value:{}|choice_timeout:{}|staple_choice:{}, measurement_repeats:{}"
                print(output_string.format(count, input_states, scale_value, choice_timeout, staple_choice, measurement_repeats))
                set_all_low()
                if 0 in input_states:
                    choice_timeout = 10
                    choice_pin = output_pins[input_states.index(0)]
                    staple_choice = staples[input_states.index(0)]
                    measurement_repeats = 0
                else:
                    if choice_pin is not None and choice_timeout > 0:
                        print(choice_pin)
                        GPIO.output(choice_pin, next(flipper))
                    else:
                        GPIO.output(next(runner), GPIO.HIGH)
                    if choice_timeout > 0:
                        choice_timeout -= 1
                    if choice_timeout == 0:
                        choice_pin = None
                        staple_choice = None
            else:
                print("Scale off.")
                staple_choice = None
                set_all_low()
                sleep(2)
            if staple_choice is not None and measurement_repeats >= 4 and scale_value != (0.0, 'g'):
                flash_all(n=5)
                print("Whoa! we just measured {}g of {}. Logging that.".format(scale_value, staple_choice))
                staple_choice = None
                set_all_low()
                measurement_repeats = 0
                choice_timeout = 0
                

    except KeyboardInterrupt:
        print("\nSetting all pins low. Exiting.")
        set_all_low()

main()
