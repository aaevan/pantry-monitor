import RPi.GPIO as GPIO
from time import sleep
from random import randint

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
        GPIO.output(8, GPIO.LOW)

def set_all_high():
    for pin in output_pins:
        GPIO.output(8, GPIO.HIGH)

def flash_all(rate=.1, n=3):
    set_all_low()
    for _ in range(n):
        GPIO.output(8, GPIO.HIGH)
        sleep(rate)
        GPIO.output(8, GPIO.LOW)
        sleep(rate)

def weighing_routine(threshold = .2):
    """
    Assumes the scale is connected.
    if not on, return False
    the LED output counts down from 5 to settle the scale
    if the scale value (once settled) changes up from zero,
    play an LED animation of 1, 12, 123, 1234, 12345 to show
    that the item is settling.
    if the value changes while the scale is counting up, 
        it does a fast blink of all LEDs and restarts the measure.
    All LEDs blink together "12345" three times when the item has settled
    the total settled weight is sent back.
    A tare weight is subtracted from the value back in main
    """
    set_all_low()
    fails = 0
    base_value = 0
    good_reading = 0
    while True:
        if fails >= 3: #if we keep messing up, it puts us back in main.
            return False
        reads = []
        set_all_low()
        for pin in output_pins: #loops over output_pins
            GPIO.output(pin, GPIO.HIGH)
            reads.append(base_value + (round(random(), 2) / 10))
            if abs(reads[-1]- base_value) > threshold:
                good_reading = False
                set_all_low()
                break
            good_reading = True
        if good_reading:
            pass
        else:
            fails += 1
            continue #if the weight changes, restart the routine

def main():
    """
    if the scale is detected, run through a looping LED animation.
    given a button press, go into weighing mode
    storing the staple that is to be weighed by which button was pressed.
    """
    count = 0
    while True:
        count = (count + 1) % 10
        input_states = [GPIO.input(pin) for pin in input_pins]
        print("({})input_states: {}".format(count, input_states))
        sleep(.2)
        """
        if input_state == True:
            flash_all()
            dummy_scale_output()
            GPIO.output(8, GPIO.HIGH)
            sleep(.2)
        else:
            GPIO.output(8, GPIO.LOW)
            sleep(.2)
        """

main()
