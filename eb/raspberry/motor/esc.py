"""
    Author: Ege Bilecen
    Date  : 02.09.2020

    Class for control a brushless motor via ESC.
"""
from time import sleep
import subprocess as subproc

class ESC:
    MIN_SPEED = 700
    MAX_SPEED = 2000

    ROTATION_BEGIN_SPEED = 1340

    def __init__(self, bcm_pin):
        self._pin = bcm_pin

        try: subproc.check_call(["sudo", "killall", "pigpiod"], stdout=subproc.DEVNULL, stderr=subproc.STDOUT)
        except subproc.CalledProcessError: pass

        subproc.check_call(["sudo", "pigpiod"], stdout=subproc.DEVNULL, stderr=subproc.STDOUT)
        sleep(1)

        import pigpio

        self._pi_gpio = pigpio.pi()
        self._pi_gpio.set_servo_pulsewidth(self._pin, 0)

    def __del__(self):
        try: self._pi_gpio.stop()
        except: pass

    def arm(self):
        self._pi_gpio.set_servo_pulsewidth(self._pin, 0)
        sleep(1)

        self._pi_gpio.set_servo_pulsewidth(self._pin, ESC.MAX_SPEED)
        sleep(1)

        self._pi_gpio.set_servo_pulsewidth(self._pin, ESC.MIN_SPEED)
        sleep(1)

    def disarm(self):
        self._pi_gpio.set_servo_pulsewidth(self._pin, 0)

    def set_speed(self, spd):
        if spd < ESC.ROTATION_BEGIN_SPEED or spd > ESC.MAX_SPEED:
            raise ValueError("Speed is out of bounds.")

        self._pi_gpio.set_servo_pulsewidth(self._pin, spd)
