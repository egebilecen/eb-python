"""
    Author: Ege Bilecen
    Date  : 15.08.2020
"""
from pymavlink import mavutil

class Copter:
    class Channel:
        ROLL        = 1
        PITCH       = 2
        THROTTLE    = 3
        YAW         = 4
        FLIGHT_MODE = 5
        OPTIONAL_1  = 6

class Enum:
    @staticmethod
    def get_int_reference(msg_str):
        return getattr(mavutil.mavlink, msg_str)

    @staticmethod
    def get_method_reference(mav, msg_str):
        return getattr(mav, msg_str.lower()+"_send")

def get_flight_modes(mavlink):
    return mavlink.mode_mapping()
