"""
    Author: Ege Bilecen
    Date  : 15.08.2020
"""
from eb.time import Time

class Telemetry:
    def __init__(self,
                 drone):
        self._drone = drone

    # Public Method(s)
    def get_boot_time(self):
        return self._drone._boot_time[0], Time.get_current_timestamp("ms") - self._drone._boot_time[1]

    def get_last_heartbeat(self, ret_diff=False):
        if ret_diff:
            return Time.get_current_timestamp("ms") - self._drone._last_heartbeat

        return self._drone._last_heartbeat

    def get_state(self):
        return self._drone._state

    def get_vehicle_type(self):
        return self._drone._vehicle_type

    def get_flight_mode(self):
        return self._drone._flight_mode

    def get_is_armed(self):
        return self._drone._armed

    def get_raw_gps(self):
        try: self._drone._gps["last_update"] = Time.get_current_timestamp("ms") - self._drone._gps["timestamp"]
        except KeyError: pass

        return self._drone._gps

    def get_attitude(self):
        try: self._drone._attitude["last_update"] = Time.get_current_timestamp("ms") - self._drone._attitude["timestamp"]
        except KeyError: pass

        return self._drone._attitude

    def get_local_position(self):
        try: self._drone._local_position["last_update"] = Time.get_current_timestamp("ms") - self._drone._local_position["timestamp"]
        except KeyError: pass

        return self._drone._local_position

    def get_global_position(self):
        try: self._drone._global_position["last_update"] = Time.get_current_timestamp("ms") - self._drone._global_position["timestamp"]
        except KeyError: pass

        return self._drone._global_position

    def get_air_speed(self):
        return self._drone._air_speed[0], Time.get_current_timestamp("ms") - self._drone._air_speed[1]

    def get_ground_speed(self):
        return self._drone._ground_speed[0], Time.get_current_timestamp("ms") - self._drone._ground_speed[1]

    def get_altitude(self):
        return self._drone._alt[0], Time.get_current_timestamp("ms") - self._drone._alt[1]

    def get_throttle(self):
        return self._drone._throttle[0], Time.get_current_timestamp("ms") - self._drone._throttle[1]

    def get_climb_rate(self):
        return self._drone._climb_rate[0], Time.get_current_timestamp("ms") - self._drone._climb_rate[1]

    def get_heading(self):
        return self._drone._heading[0], Time.get_current_timestamp("ms") - self._drone._heading[1]

    # TODO
    def get_is_armable(self):
        raise NotImplementedError

    def get_battery(self):
        self._drone._battery["last_update"] = Time.get_current_timestamp("ms") - self._drone._battery["timestamp"]

        return self._drone._battery
