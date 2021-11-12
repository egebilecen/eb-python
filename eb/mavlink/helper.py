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
        AUX_1       = 7
        AUX_2       = 8
        AUX_3       = 9
        AUX_4       = 10
        AUX_5       = 11
        AUX_6       = 12
        AUX_7       = 13
        AUX_8       = 14

class Enum:
    @staticmethod
    def get_int_reference(msg_str):
        return getattr(mavutil.mavlink, msg_str)

    @staticmethod
    def get_method_reference(mav, msg_str):
        return getattr(mav, msg_str.lower()+"_send")

def get_flight_modes(mavlink):
    return mavlink.mode_mapping()
