import RPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(9, GPIO.OUT, initial=GPIO.LOW)

while True:

