"""
    Author: Ege Bilecen
    Date  : 15.08.2020
"""
from eb.drone.mission import Mission

class Convert:
    @staticmethod
    def custom_mode_to_str(mode, mode_list):
        try:    return list(mode_list.keys())[mode]
        except: return "UNKNOWN"

    @staticmethod
    def state_to_str(state):
        if state == 0: return "UNINITIALIZED"
        if state == 1: return "BOOT"
        if state == 2: return "CALIBRATE"
        if state == 3: return "STANDBY"
        if state == 4: return "ACTIVE"
        if state == 5: return "CRITICAL"
        if state == 6: return "EMERGENCY"
        if state == 7: return "POWEROFF"
        if state == 8: return "TERMINATE"

        return "UNKNOWN"

    @staticmethod
    def vehicle_type_to_str(vehicle_type):
        if vehicle_type ==  0: return "GENERIC"
        if vehicle_type ==  1: return "FIXED_WING"
        if vehicle_type ==  2: return "QUADROTOR"
        if vehicle_type ==  3: return "COAXIAL_HELICOPTER"
        if vehicle_type ==  4: return "NORMAL_HELICOPTER"
        if vehicle_type ==  7: return "AIRSHIP"
        if vehicle_type ==  8: return "FREE_BALLOON"
        if vehicle_type ==  9: return "ROCKET"
        if vehicle_type == 10: return "GROUND_ROVER"
        if vehicle_type == 11: return "SURFACE_BOAT"
        if vehicle_type == 12: return "SUBMARINE"
        if vehicle_type == 13: return "HEXAROTOR"
        if vehicle_type == 14: return "OCTOROTOR"
        if vehicle_type == 15: return "TRICOPTER"
        if vehicle_type == 16: return "FLAPPING_WING"
        if vehicle_type == 17: return "KITE"

        return "UNKNOWN"

    @staticmethod
    def mission_type_str_to_int(mission_type_str):
        mission_type_str = mission_type_str.upper()

        if mission_type_str == "TAKEOFF"        : return Mission.Type.TAKEOFF
        if mission_type_str == "LAND"           : return Mission.Type.LAND
        if mission_type_str == "WAYPOINT"       : return Mission.Type.WAYPOINT
        if mission_type_str == "SPLINE_WAYPOINT": return Mission.Type.SPLINE_WAYPOINT
        if mission_type_str == "HOME_POINT"     : return Mission.Type.HOME_POINT

        return Mission.Type.UNKNOWN
