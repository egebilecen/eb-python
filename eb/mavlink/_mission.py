"""
    Author: Ege Bilecen
    Date  : 15.08.2020
"""
from time import sleep
import threading
import os

from eb.logger import Logger
from eb.method import Method
from eb.time   import Time

class Mission:
    def __init__(self, vehicle, scripts_dir, control_rate):
        self.LOG_INFO = "_mission.py"

        self._vehicle      = vehicle
        self._scripts_dir  = scripts_dir
        self._control_rate = control_rate

        # Mission Settings
        self._pos_update_interval   = 250 # ms
        self._mission_retries       = 20
        self._mission_retry_timeout = 500
        self._wp_radius             = 0 # m, waypoint accept radius

        self._mission_list = []
        self._current_mission_index  = -1
        self._current_running_script = ""

        # 0 - Idle
        # 1 - Running mission
        # 2 - Mission paused
        self._status = 0

    class Type:
        UNKNOWN         = 0
        TAKEOFF         = 1
        LAND            = 2
        WAYPOINT        = 3
        SPLINE_WAYPOINT = 4
        HOME_POINT      = 5

        @staticmethod
        def get_str(mission_type):
            if mission_type == Mission.Type.TAKEOFF:         return "TAKEOFF"
            if mission_type == Mission.Type.LAND:            return "LAND"
            if mission_type == Mission.Type.WAYPOINT:        return "WAYPOINT"
            if mission_type == Mission.Type.SPLINE_WAYPOINT: return "SPLINE_WAYPOINT"
            if mission_type == Mission.Type.HOME_POINT:      return "HOME_POINT"

            return "UNKNOWN"

    class _Proto:
        def __init__(self, mission_type=None, lat=0., lon=0., alt=0., delay=0., script=""):
            if  mission_type != Mission.Type.TAKEOFF         \
            and mission_type != Mission.Type.LAND            \
            and mission_type != Mission.Type.WAYPOINT        \
            and mission_type != Mission.Type.SPLINE_WAYPOINT \
            and mission_type != Mission.Type.HOME_POINT:
                raise TypeError("Invalid mission type.")

            if alt   < 0: raise ValueError("Altitude is negative.")
            if delay < 0: raise ValueError("Delay is negative.")

            self._type   = mission_type
            self._lat    = lat
            self._lon    = lon
            self._alt    = alt
            self._delay  = delay
            self._script = script
            self._status = 0 # 0 - Not started, 1 - Started, 2 - Completedt
            self._storage = {}

        def get(self, var_name):
            return getattr(self, "_"+var_name)

        def set(self, var_name, val):
            if var_name == "status": self._status = val
            else:
                raise AttributeError("Only status can be assigned.")

        def set_storage_variable(self, key, val):
            self._storage[key] = val

        def get_storage_variable(self, key):
            if key not in self._storage: return None

            return self._storage[key]

    # Private Method(s)
    @staticmethod
    def _thread_handler(cls):
        LOG_INFO = cls.LOG_INFO + " - _thread_handler()"

        Logger.PrintLog(LOG_INFO, "Mission tracker thread has started.")

        emergency_mode = "LAND"
        set_to_emergency_mode = False

        while cls.get_status() == 1:
            try:
                is_completed = False
                current_mission_index = cls.get_current_mission_index()
                current_mission       = cls._mission_list[current_mission_index]
                current_flight_mode   = cls._vehicle.telemetry().get_flight_mode()

                if current_flight_mode != "GUIDED" \
                and (current_flight_mode != "LAND" and current_mission.get("type") != Mission.Type.LAND):
                    Logger.PrintLog(LOG_INFO, "Flight mode has changed from GUIDED mode. Stopping. Current flight mode: {}."
                                    .format(current_flight_mode))
                    break

                if current_mission.get("status") == 0:
                    global_pos = cls._vehicle.telemetry().get_global_position()

                    current_mission.set_storage_variable("rel_alt",  global_pos["relative_alt"])
                    current_mission.set_storage_variable("start_ms", Time.get_current_timestamp("ms"))
                    current_mission.set_storage_variable("retries",  0)

                    res = cls._execute_mission(current_mission,
                                               cls._mission_retries,
                                               cls._mission_retry_timeout)

                    if not res:
                        Logger.PrintLog(LOG_INFO, "_execute_mission() has failed. Stopping. Current mission index: {}."
                                        .format(str(current_mission_index)))

                        set_to_emergency_mode = True
                        break

                    Logger.PrintLog(LOG_INFO, "Tracking the mission at index {}, type {}."
                                    .format(str(current_mission_index),
                                            Mission.Type.get_str(current_mission.get("type"))))

                    cls._mission_list[current_mission_index].set("status", 1)
                # .\mission command execution

                if current_mission.get("type") == Mission.Type.TAKEOFF:
                    Logger.PrintLog(LOG_INFO, "Tracking TAKEOFF mission status.")

                    desired_alt = current_mission.get("alt")
                    threshold   = 0.5

                    if cls._vehicle.control().is_reached_to_relative_alt(desired_alt, threshold):
                        is_completed = True
                elif current_mission.get("type") == Mission.Type.LAND:
                    Logger.PrintLog(LOG_INFO, "Tracking LAND mission status.")
                    threshold = 0.5

                    if cls._vehicle.control().is_reached_to_relative_alt(0, threshold):
                        is_completed = True
                elif current_mission.get("type") == Mission.Type.WAYPOINT:
                    Logger.PrintLog(LOG_INFO, "Tracking WAYPOINT mission status.")

                    dest_pos = {
                        "lat" : current_mission.get("lat"),
                        "lon" : current_mission.get("lon")
                    }

                    desired_alt = current_mission.get("alt")
                    threshold   = 0.15

                    cls._execute_mission(current_mission,
                                         cls._mission_retries,
                                         cls._mission_retry_timeout)

                    if cls._vehicle.control().is_reached_to_global_position(dest_pos["lat"], dest_pos["lon"], desired_alt, threshold, cls._wp_radius):
                        is_completed = True
                elif current_mission.get("type") == Mission.Type.HOME_POINT:
                    is_completed = True
                # .\mission controls

                if not is_completed:
                    # not used currently
                    current_mission.set_storage_variable("retries",
                                                         current_mission.get_storage_variable("retries") + 1)
                else:
                    Logger.PrintLog(LOG_INFO, "Mission at index {}, type {} has completed."
                                    .format(str(cls.get_current_mission_index()),
                                            Mission.Type.get_str(current_mission.get("type"))))

                    script = current_mission.get("script")

                    if script != "":
                        script = script + ".py"
                        script_path = cls._scripts_dir + script

                        if os.path.isfile(script_path):
                            with open(script_path, "r") as f:
                                Logger.PrintLog(LOG_INFO, "Executing script {}."
                                                .format(script))

                                cls._current_running_script = script
                                exec_return = {}

                                hold_pos = {"hold" : True}
                                cls._vehicle.action().hold_global_position(hold_pos, cls._pos_update_interval)

                                try:
                                    exec(compile(f.read(), script, "exec"), {
                                        "vehicle" : cls._vehicle,
                                        "control" : {
                                            "position" : {
                                                "hold" : hold_pos
                                            }
                                        }
                                    }, exec_return)
                                except Exception as ex:
                                    Logger.PrintLog(LOG_INFO, "An exception occured while running {}. Exception: {} - {}. Proceeding to next mission if there is."
                                                    .format(script, type(ex).__name__, str(ex)))

                                Logger.PrintLog(LOG_INFO, "Script executed. Returned data: {}"
                                                .format(str(exec_return.get("return_val", {}))))

                                hold_pos["hold"] = False
                                Method.Dict.wait_until_value(hold_pos, "ended", True)
                        else:
                            Logger.PrintLog(LOG_INFO, "Cannot find script {} in scripts path ({}). Skipping."
                                            .format(script, cls._scripts_dir))

                    cls._current_running_script = ""
                    cls._mission_list[current_mission_index].set("status", 2)

                    if current_mission_index != cls.get_mission_count() - 1:
                        cls._current_mission_index += 1
                    else:
                        Logger.PrintLog(LOG_INFO, "All missions are successfully finished.")

                        if cls._mission_list[-1].get("type") != Mission.Type.LAND:
                            set_to_emergency_mode = True

                        break

                    if current_mission.get("delay") != 0:
                        Logger.PrintLog(LOG_INFO, "Delaying the next mission for {} seconds."
                                        .format(current_mission.get("delay")))

                        hold_pos = {"hold" : True}
                        cls._vehicle.action().hold_global_position(hold_pos, cls._pos_update_interval)

                        delay_timestamp = Time.get_current_timestamp("ms")

                        while 1:
                            time_diff = Time.get_current_timestamp("ms") - delay_timestamp

                            if time_diff >= current_mission.get("delay") * 1000:
                                break

                        Logger.PrintLog(LOG_INFO, "Delay has ended.")

                        hold_pos["hold"] = False
                        Method.Dict.wait_until_value(hold_pos, "ended", True)

                    continue
                # .\is mission completed check

                sleep(1 / cls._control_rate)
            except Exception as ex:
                Logger.PrintException(LOG_INFO, ex)

                set_to_emergency_mode = True
                break
        # .\while

        if cls.get_status() == 2:
            Logger.PrintLog(LOG_INFO, "Mission at index {} is paused."
                            .format(str(cls.get_current_mission_index())))
            cls._mission_list[cls.get_current_mission_index()].set("status",      0)
            cls._mission_list[cls.get_current_mission_index()].set("is_uploaded", 0)

        if cls.get_status() != 2:
            cls._status = 0

        if set_to_emergency_mode:
            Logger.PrintLog(LOG_INFO, "!!! EMERGENCY SITUATION DETECTED !!! Setting flight mode to {}."
                            .format(emergency_mode))
            cls._vehicle.action().set_flight_mode(emergency_mode)

        Logger.PrintLog(LOG_INFO, "Mission tracker thread has ended.")

    def _execute_mission(self, mission, retries=5, timeout=1000):
        Logger.PrintLog(self.LOG_INFO, "_execute_mission() - Executing mission. Mission type: {}."
                        .format(Mission.Type.get_str(mission.get("type"))))

        # https://mavlink.io/en/messages/common.html#MAV_CMD_NAV_TAKEOFF
        if mission.get("type") == Mission.Type.TAKEOFF:
            return self._vehicle.action().takeoff(mission.get("alt"), retries=retries, timeout=timeout)

        # https://mavlink.io/en/messages/common.html#MAV_CMD_NAV_LAND
        elif mission.get("type") == Mission.Type.LAND:
            return self._vehicle.action().land(retries=retries, timeout=timeout)

        # https://mavlink.io/en/messages/common.html#SET_POSITION_TARGET_GLOBAL_INT
        # https://mavlink.io/en/messages/common.html#MAV_CMD_NAV_WAYPOINT
        # https://github.com/ArduPilot/MAVProxy/blob/b2452edc85c6d8c83cc258e3e6219ac9b1268675/MAVProxy/modules/mavproxy_mode.py#L73
        # https://github.com/dronekit/dronekit-python/blob/master/dronekit/__init__.py#L2187
        elif mission.get("type") == Mission.Type.WAYPOINT:
            return self._vehicle.action().go_to_global_position(mission.get("lat"),
                                                              mission.get("lon"),
                                                              mission.get("alt"))

        elif mission.get("type") == Mission.Type.SPLINE_WAYPOINT:
            raise NotImplementedError

        # https://mavlink.io/en/messages/common.html#MAV_CMD_DO_SET_HOME
        elif mission.get("type") == Mission.Type.HOME_POINT:
            return self._vehicle.action().set_home_position(retries=retries, timeout=timeout)

        else: raise TypeError("Invalid mission type.")

    # Public Method(s)
    @staticmethod
    def get_mission_item_proto(mission_type=None, lat=0., lon=0., alt=0., delay=0., script=""):
        return Mission._Proto(mission_type, lat, lon, alt, delay, script)

    def add_mission_item_proto(self, proto):
        if not isinstance(proto, Mission._Proto): raise ValueError("proto argument is not instance of Mission._Proto.")

        self._mission_list.append(proto)

    def clear_list(self):
        Logger.PrintLog(self.LOG_INFO, "clear_list() - Clearing mission list.")

        if self.get_status() == 1:
            Logger.PrintLog(self.LOG_INFO, "clear_list() - Cannot clear mission list. Current status is {}."
                            .format(str(self._status)))
            return False

        self._mission_list = []
        self._current_mission_index  = -1
        self._current_running_script = ""

        return True

    def start(self):
        Logger.PrintLog(self.LOG_INFO, "start() - Starting mission(s).")

        global_pos = self._vehicle.telemetry().get_global_position()

        if len(self._mission_list) < 1:
            Logger.PrintLog(self.LOG_INFO, "start() - Cannot start mission(s). There is no mission to start.")
            return False
        elif self.get_status() != 0 \
        and  self.get_status() != 2:
            Logger.PrintLog(self.LOG_INFO, "start() - Cannot start the mission(s). Current status is {}."
                            .format(str(self._status)))
            return False
        elif global_pos == {}:
            Logger.PrintLog(self.LOG_INFO, "start() - Cannot start the mission(s). Global position information is not set yet.")
            return False
        elif self._vehicle.telemetry().get_local_position() == {}:
            Logger.PrintLog(self.LOG_INFO, "start() - Cannot start the mission(s). Local position information is not set yet.")
            return False
        elif self._vehicle.telemetry().get_flight_mode() == "AUTO":
            Logger.PrintLog(self.LOG_INFO, "start() - Cannot start the mission(s). Current flight mode is AUTO.")
            return False

        if self._mission_list[0].get("type") != Mission.Type.HOME_POINT:
            self._mission_list.insert(0, self.get_mission_item_proto(mission_type = Mission.Type.HOME_POINT))

        if not self._vehicle.telemetry().get_is_armed():
            Logger.PrintLog(self.LOG_INFO, "start() - Vehicle is not armed. Attempting to arm.")

            res = self._vehicle.action().arm()

            if res:
                Logger.PrintLog(self.LOG_INFO, "start() - Successfully armed. Waiting for 3 seconds and then proceeding.")
                sleep(3)
            else:
                Logger.PrintLog(self.LOG_INFO, "start() - Couldn't arm the vehicle. Stopping.")
                return False

        res = self._vehicle.action().set_flight_mode("GUIDED")

        if not res:
            Logger.PrintLog(self.LOG_INFO, "start() - Couldn't get into GUIDED flight mode. Stopping.")
            return False

        self._vehicle.set_variable("eb_home_pos",
                                 (global_pos["lat"], global_pos["lon"]))

        if self._current_mission_index == -1:
            self._current_mission_index = 0

        self._current_running_script = ""
        self._status = 1

        _ = threading.Thread(target=Mission._thread_handler, args=(self,))
        _.daemon = False
        _.start()

        return True

    def reset(self):
        Logger.PrintLog(self.LOG_INFO, "reset() - Resetting missions to their first states.")

        if self.get_status() == 1:
            Logger.PrintLog(self.LOG_INFO, "reset() - Cannot reset mission(s). Status must be 0 or 2.")
            return False

        for mission in self._mission_list:
            if mission.get("type") != Mission.Type.HOME_POINT:
                mission.set("status", 0)

        self._current_mission_index  = -1
        self._current_running_script = ""

    # Running script should check if mission status is 1 to continue it's process.
    # If mission status is not 1, then it should terminate the execution.
    def abort(self):
        Logger.PrintLog(self.LOG_INFO, "abort() - Aborting the mission(s).")

        if  self.get_status() != 1 \
        and self.get_status() != 2:
            Logger.PrintLog(self.LOG_INFO, "abort() - Cannot abort the mission(s). Current status is {}."
                            .format(str(self._status)))
            return False

        self.stop()
        self.clear_list()

        return True

    def stop(self):
        Logger.PrintLog(self.LOG_INFO, "stop() - Stopping mission(s).")

        if self.get_status() != 1:
            Logger.PrintLog(self.LOG_INFO, "stop() - Cannot stop the mission(s). Current status is {}."
                            .format(str(self._status)))
            return False

        self._vehicle.action().set_flight_mode("LOITER")
        self._status = 2

        return True

    def export(self, file_name):
        Logger.PrintLog(self.LOG_INFO, "export() - Exporting mission(s) to {}. Output directory: {}."
                        .format(file_name, self._vehicle.get_output_directory()))

        if len(self._mission_list) < 1:
            Logger.PrintLog(self.LOG_INFO, "export() - There is no mission to export.")
            return False

        if not os.path.isdir(self._vehicle.get_output_directory()):
            Logger.PrintLog(self.LOG_INFO, "export() - Output directory is not exist.")
            return False

        mission_str = ""

        for i, mission in enumerate(self._mission_list):
            mission_str += str(mission.get("type"))  + ","
            mission_str += str(mission.get("lat"))   + ","
            mission_str += str(mission.get("lon"))   + ","
            mission_str += str(mission.get("alt"))   + ","
            mission_str += str(mission.get("delay")) + ","
            mission_str += str(mission.get("script"))

            if i != len(self._mission_list) - 1:
                mission_str += "|"

        file_location = self._vehicle.get_output_directory() + file_name
        with open(file_location, "w") as f:
            f.write(mission_str)

        Logger.PrintLog(self.LOG_INFO, "export() - Mission successfully exported. Location: {}."
                        .format(file_location))
        return True

    def load(self, file_name):
        Logger.PrintLog(self.LOG_INFO, "load() - Loading mission from {}. Directory: {}."
                        .format(file_name, self._vehicle.get_output_directory()))

        file_location = self._vehicle.get_output_directory() + file_name

        if not os.path.isfile(file_location):
            Logger.PrintLog(self.LOG_INFO, "load() - File is not exist in directory.")
            return False

        res = self.clear_list()

        if not res:
            Logger.PrintLog(self.LOG_INFO, "load() - Couldn't clear the mission list. Aborting.")
            return False

        with open(file_location, "r") as f:
            list_str = f.read()

            for mission in list_str.split("|"):
                mission_split = mission.split(",")

                self._mission_list.append(self.get_mission_item_proto(
                    mission_type = int(mission_split[0]),
                    lat          = float(mission_split[1]),
                    lon          = float(mission_split[2]),
                    alt          = float(mission_split[3]),
                    delay        = float(mission_split[4]),
                    script       = mission_split[5]
                ))

        return True

    # alt - relative to frame
    def add_takeoff_mission(self, alt, delay=0, script=""):
        Logger.PrintLog(self.LOG_INFO, "add_takeoff_mission() - Adding takeoff mission to local list.")

        self._mission_list.append(self.get_mission_item_proto(
            mission_type = Mission.Type.TAKEOFF,
            alt          = alt,
            delay        = delay,
            script       = script
        ))

    def add_land_mission(self, delay=0, script=""):
        Logger.PrintLog(self.LOG_INFO, "add_land_mission() - Adding land mission to local list.")

        self._mission_list.append(self.get_mission_item_proto(
            mission_type = Mission.Type.LAND,
            delay        = delay,
            script       = script
        ))

    # lat, lon - Global Position
    # alt - Relative to frame
    def add_waypoint_mission(self, lat, lon, alt, delay=0, script=""):
        Logger.PrintLog(self.LOG_INFO, "add_waypoint_mission() - Adding waypoint mission to local list.")

        self._mission_list.append(self.get_mission_item_proto(
            mission_type = Mission.Type.WAYPOINT,
            lat          = lat,
            lon          = lon,
            alt          = alt,
            delay        = delay,
            script       = script
        ))

    def set_waypoint_radius(self, size):
        if size < 0: raise ValueError

        self._wp_radius = size

    def get_status(self):
        return self._status

    def get_mission_count(self):
        mission_count = len(self._mission_list)

        if mission_count < 1: return 0

        return mission_count

    def get_current_mission_index(self):
        return self._current_mission_index

    def get_current_running_script(self):
        return self._current_running_script
