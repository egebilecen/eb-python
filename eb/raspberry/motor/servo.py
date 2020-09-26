"""
    Author: Ege Bilecen
    Date  : 01.09.2020
"""
from time import sleep
import RPi.GPIO as GPIO

from eb.math import Math

class Servo:
    class Degree180:
        # Below values must be found manually.
        MIN_DUTY_CYCLE = 1.25
        MAX_DUTY_CYCLE = 12.5

        def __init__(self,
                     pin: int):
            self._pin = pin

            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BOARD)
            GPIO.setup(self._pin, GPIO.OUT)

            self._pwm = GPIO.PWM(self._pin, 50)
            self._pwm.start(0)

        def set_angle(self,
                      angle: int,
                      wait_duration: int = 1000):
            self._pwm.ChangeDutyCycle(Math.Value.map(angle,
                                                     0, 180,
                                                     Servo.Degree180.MIN_DUTY_CYCLE, Servo.Degree180.MAX_DUTY_CYCLE))
            sleep(wait_duration / 1000)
            self._pwm.ChangeDutyCycle(0)