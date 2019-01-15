import ast
from datetime import date
from itertools import cycle
from random import randint, random
from read_scale import *
import RPi.GPIO as GPIO
from time import sleep

log_filename = 'staple_log.txt'
current_working_directory = os.getcwd()

#the values specified here will be written as the starting values of each staple:
staples = {'black beans':1000.0, 'brown rice':999.0, 'flour':800.0, 'kosher salt':500.0, 'MSG':300.0}
index_to_staple = {0:'black beans', 1:'brown rice', 2:'flour', 3:'kosher salt', 4:'MSG'}
#weigh out each of the containers to be used for each staple and enter the gram amounts here:
tares =   {'black beans':100.0, 'brown rice':110.0, 'flour':120.0, 'kosher salt':104.0, 'MSG':80.0}

print(index_to_staple)

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
output_pins = (8, 10, 12, 16, 18)
input_pins = (29, 31, 33, 35, 37)
runner = cycle(output_pins)
flipper = cycle((GPIO.HIGH, GPIO.LOW))

for pin in output_pins:
    GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
for pin in input_pins:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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

def logging_routine(scale_value=None, staple_choice=None):
    #TODO: figure out a way to log the last values of each staple.
    # once every 10 minutes, check whether the last line in the log file has changed, if so, 
    # write a new line with the updated gram values
    # determine the average rate of change for the last many values (logged every day at noon?)
    # and determine roughly when the staple will run out.
    # TODO: account for tare values in the logged measurements.
    # TODO: fire off the most recent measures to a push notification.
    if scale_value is None or staple_choice is None:
        return False
    print("Measured {}g of {}. Logging that.".format(scale_value[0], staple_choice))
    log_path = "{}/{}".format(current_working_directory, log_filename)
    print("log_path:{}".format(log_path))
    #initialize the log if it doesn't already exist:
    if not os.path.exists(log_path):
        with open(log_path, 'x') as log:
            log.write(str(staples) + "\n")
    #get the current contents of the log:
    log_contents = []
    with open(log_path, 'r') as log:
        for line in log:
            line_text = log.read()
            print(line_text)
            log_contents.append(line_text)
    last_line = log_contents[-1]
    #write the most recent values to the log (TODO: along with the current date)
    staples[staple_choice] = scale_value[0]
    with open(log_path, 'a') as log:
        log.write(str(staples) + '\n')

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
            #if value is changing, give the user more time:
            elif scale_value != last_measure and staple_choice is not None:
                choice_timeout += 2
            else:
                measurement_repeats = 0
            #given a scale that's on:
            if scale_value is not None:
                #print a big debug string:
                output_string = "count:{}|input_states:{}|scale_value:{}|choice_timeout:{}|staple_choice:{}, measurement_repeats:{}"
                print(output_string.format(count, input_states, scale_value, choice_timeout, staple_choice, measurement_repeats))
                set_all_low()
                #if a switch is pressed, get ready for measurement of a particular staple:
                if 0 in input_states:
                    choice_timeout = 10
                    choice_pin = output_pins[input_states.index(0)]
                    staple_choice = index_to_staple[input_states.index(0)]
                    measurement_repeats = 0
                else:
                    if choice_pin is not None and choice_timeout > 0:
                        print(choice_pin)
                        #blink the selected pin:
                        GPIO.output(choice_pin, next(flipper))
                    else:
                        #otherwise display an idle animation:
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
                #write to the log file:
                logging_routine(scale_value=scale_value, staple_choice=staple_choice)
                #clear out old values:
                staple_choice = None
                set_all_low()
                measurement_repeats = 0
                choice_timeout = 0
    except KeyboardInterrupt:
        print("\nSetting all pins low. Exiting.")
        set_all_low()

main()
