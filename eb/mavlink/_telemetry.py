"""
    Author: Ege Bilecen
    Date  : 15.08.2020
"""
from eb.time import Time

class Telemetry:
    def __init__(self,
                 vehicle):
        self._vehicle = vehicle

    # Public Method(s)
    def get_boot_time(self):
        return self._vehicle._boot_time[0], Time.get_current_timestamp("ms") - self._vehicle._boot_time[1]

    def get_last_heartbeat(self, ret_diff=False):
        if ret_diff:
            return Time.get_current_timestamp("ms") - self._vehicle._last_heartbeat

        return self._vehicle._last_heartbeat

    def get_state(self):
        return self._vehicle._state

    def get_vehicle_type(self):
        return self._vehicle._vehicle_type

    def get_flight_mode(self):
        return self._vehicle._flight_mode

    def get_is_armed(self):
        return self._vehicle._armed

    def get_raw_gps(self):
        try: self._vehicle._gps["last_update"] = Time.get_current_timestamp("ms") - self._vehicle._gps["timestamp"]
        except KeyError: pass

        return self._vehicle._gps

    def get_attitude(self):
        try: self._vehicle._attitude["last_update"] = Time.get_current_timestamp("ms") - self._vehicle._attitude["timestamp"]
        except KeyError: pass

        return self._vehicle._attitude

    def get_local_position(self):
        try: self._vehicle._local_position["last_update"] = Time.get_current_timestamp("ms") - self._vehicle._local_position["timestamp"]
        except KeyError: pass

        return self._vehicle._local_position

    def get_global_position(self):
        try: self._vehicle._global_position["last_update"] = Time.get_current_timestamp("ms") - self._vehicle._global_position["timestamp"]
        except KeyError: pass

        return self._vehicle._global_position

    def get_air_speed(self):
        return self._vehicle._air_speed[0], Time.get_current_timestamp("ms") - self._vehicle._air_speed[1]

    def get_ground_speed(self):
        return self._vehicle._ground_speed[0], Time.get_current_timestamp("ms") - self._vehicle._ground_speed[1]

    def get_altitude(self):
        return self._vehicle._alt[0], Time.get_current_timestamp("ms") - self._vehicle._alt[1]

    def get_throttle(self):
        return self._vehicle._throttle[0], Time.get_current_timestamp("ms") - self._vehicle._throttle[1]

    def get_climb_rate(self):
        return self._vehicle._climb_rate[0], Time.get_current_timestamp("ms") - self._vehicle._climb_rate[1]

    def get_heading(self):
        return self._vehicle._heading[0], Time.get_current_timestamp("ms") - self._vehicle._heading[1]

    # TODO
    def get_is_armable(self):
        raise NotImplementedError

    def get_battery(self):
        self._vehicle._battery["last_update"] = Time.get_current_timestamp("ms") - self._vehicle._battery["timestamp"]

        return self._vehicle._battery

    def get_raw_rc_channel_values(self):
        try: self._vehicle._raw_rc_channels["last_update"] = Time.get_current_timestamp("ms") - self._vehicle._raw_rc_channels["timestamp"]
        except KeyError: pass

        return self._vehicle._raw_rc_channels
