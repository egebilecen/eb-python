"""
    Author: Ege Bilecen
    Date  : 15.08.2020

    Notes:
    * All method parameters related to time are based on milliseconds.
"""
from pymavlink import mavutil
import threading

from eb.time   import Time
from eb.method import Method
from eb.logger import Logger

from eb.mavlink._telemetry import Telemetry
from eb.mavlink._action    import Action
from eb.mavlink._mission   import Mission
from eb.mavlink._control   import Control
from eb.mavlink.convert    import Convert
import eb.mavlink.helper as eb_mavutil

class Vehicle:
    def __init__(self,
                 port_name            : str  = "/dev/ttyTHS1",
                 baudrate             : int  = 115200,
                 timeout              : int  = 5000,
                 rate                 : int  = 2,  # hz
                 source_system        : int  = 255,
                 source_component     : int  = 0,
                 retries              : int  = 3,
                 autoreconnect        : bool = False,
                 scripts_dir          : str  = "",
                 mission_control_rate : int  = 4,
                 output_dir           : str  = "./") -> None:
        start_timestamp = Time.get_current_timestamp("ms")

        self._mavlink = mavutil.mavlink_connection(port_name,
                                                   baud             = baudrate,
                                                   source_system    = source_system,
                                                   source_component = source_component,
                                                   retries          = retries,
                                                   autoreconnect    = autoreconnect)
        # Variables
        self.LOG_INFO    = "vehicle.py"
        self._output_dir = output_dir
        self._rate       = rate
        self._variables  = {}
        self._first_arm  = True

        self._message_request_list = {
            "SYS_STATUS"          : {"ref_int" :  1},
            "SYSTEM_TIME"         : {"ref_int" :  2},
            "GPS_RAW_INT"         : {"ref_int" : 24},
            "ATTITUDE"            : {"ref_int" : 30},
            "LOCAL_POSITION_NED"  : {"ref_int" : 32},
            "GLOBAL_POSITION_INT" : {"ref_int" : 33},
            "RC_CHANNELS_RAW"     : {"ref_int" : 35},
            "VFR_HUD"             : {"ref_int" : 74}
        }

        # All the variables below will be populated, see _thread_handler().
        self._messages = {
            "COMMAND_ACK" : {}
        }
        self._boot_time      = 0 # ms
        self._last_heartbeat = 0 # ms

        ### Accessable through telemetry()
        self._state           = "UNKNOWN"
        self._vehicle_type    = "UNKNOWN"
        self._flight_mode     = "UNKNOWN"
        self._armed           = False
        self._gps             = {}
        self._attitude        = {}
        self._local_position  = {}
        self._global_position = {}
        self._raw_rc_channels = {}
        self._battery         = {}
        self._air_speed       = None
        self._ground_speed    = None
        self._heading         = None
        self._alt             = None
        self._throttle        = None
        self._climb_rate      = None
        self._exception       = None

        # Classes
        self._action    = Action   (self)
        self._telemetry = Telemetry(self)
        self._mission   = Mission  (self, scripts_dir, mission_control_rate)
        self._control   = Control  (self)

        # Start message handler
        _ = threading.Thread(target=Vehicle._thread_handler, args=(self,))
        _.daemon = False
        _.start()

        Logger.PrintLog(self.LOG_INFO, "__init__() - Connecting to vehicle.")

        while "HEARTBEAT" not in self._messages \
        or    self._exception is not None:
            if self._exception is not None:
                raise self._exception
            elif Time.get_current_timestamp("ms") - start_timestamp >= timeout:
                raise TimeoutError("Couldn't detect heartbeat in {} milliseconds."
                                   .format(str(timeout)))

        Logger.PrintLog(self.LOG_INFO, "__init__() - Successfully connected to vehicle.")

        # Request Messages
        def _set_message_intervals(cls):
            Logger.PrintLog(cls.LOG_INFO, "_set_message_intervals() - Setting message intervals.")
            for msg_str in cls._message_request_list:
                cls._set_message_interval(cls._message_request_list[msg_str]["ref_int"], 1000 / self._rate)

        _ = threading.Thread(target=_set_message_intervals, args=(self,))
        _.daemon = False
        _.start()

    # Private Method(s)
    def _get_target_system(self):
        return self.mavlink().target_system

    def _get_target_component(self):
        return self.mavlink().target_component

    def _set_message_interval(self, msg_id, interval_ms=1000, retries=8, timeout=500):
        def impl():
            COMMAND = eb_mavutil.Enum.get_int_reference("MAV_CMD_SET_MESSAGE_INTERVAL")

            self.mav().command_long_send(
                self._get_target_system(),
                self._get_target_component(),
                COMMAND,
                0,
                # params
                msg_id, interval_ms * (10 ** 3), 0, 0, 0, 0, 0
            )

            res = self.wait_cmd_ack(COMMAND, timeout)

            if res == 0: 
                Logger.PrintLog(self.LOG_INFO, "_set_message_interval() - Message interval sucessfully set for {}.".format(msg_id))
                return True
            else:
                Logger.PrintLog(self.LOG_INFO, "_set_message_interval() - Setting message interval failed for {}.".format(msg_id))
                return False

        interval_res = Method.Repeat.until_value(impl, (), retries, ret_val=True)[0]

        if not interval_res: return False

        return True

    def _request_message(self, msg_id, retries=8, timeout=500):
        def impl():
            COMMAND = eb_mavutil.Enum.get_int_reference("MAV_CMD_REQUEST_MESSAGE")

            self.mav().command_long_send(
                self._get_target_system(),
                self._get_target_component(),
                COMMAND,
                0,
                # params
                msg_id,
                0, 0, 0, 0, 0,
                0
            )

            res = self.wait_cmd_ack(COMMAND, timeout)

            if res == 0: return True
            else:        return False

        request_res = Method.Repeat.until_value(impl, (), retries, ret_val=True)[0]

        if not request_res: return False

        return True

    # https://mavlink.io/en/messages/common.html
    @staticmethod
    def _thread_handler(cls):
        # LOG_INFO = cls.LOG_INFO + "_thread_handler() - "

        while 1:
            try:
                msg_packet = cls.mavlink().recv_match()
            except Exception as ex:
                cls._exception = ex
                return

            if not msg_packet: continue

            msg_packet = msg_packet.to_dict()
            msg_packet["eb_timestamp"] = Time.get_current_timestamp("ms")

            packet_type = msg_packet["mavpackettype"]

            # HEARTBEAT
            if packet_type == "HEARTBEAT":
                cls._last_heartbeat = msg_packet["eb_timestamp"]
                cls._state          = Convert.state_to_str(msg_packet["system_status"])
                cls._vehicle_type   = Convert.vehicle_type_to_str(msg_packet["type"])
                cls._flight_mode    = Convert.custom_mode_to_str(msg_packet["custom_mode"],
                                                                 eb_mavutil.get_flight_modes(cls.mavlink()))
                if msg_packet["base_mode"] & 128:
                    cls._armed = True
                else: cls._armed = False

            # SYS_STATUS
            elif packet_type == "SYS_STATUS":
                cls._battery = {
                    "voltage"   : msg_packet["voltage_battery"] / (10 ** 3), # V
                    "current"   : msg_packet["current_battery"] / (10 ** 2), # A
                    "remaining" : msg_packet["battery_remaining"],           # %
                    "timestamp" : msg_packet["eb_timestamp"]
                }

            # SYSTEM_TIME
            elif packet_type == "SYSTEM_TIME":
                cls._boot_time = (msg_packet["time_boot_ms"], msg_packet["eb_timestamp"])

            # GPS_RAW_INT
            elif packet_type == "GPS_RAW_INT":
                cls._gps = {
                    "fix_type"  : msg_packet["fix_type"],
                    "lat"       : msg_packet["lat"] / (10 ** 7), # degree
                    "lon"       : msg_packet["lon"] / (10 ** 7), # degree
                    "alt"       : msg_packet["alt"] / (10 ** 3), # meters
                    "sat_count" : msg_packet["satellites_visible"],
                    "timestamp" : msg_packet["eb_timestamp"]
                }

            # ATTITUDE
            elif packet_type == "ATTITUDE":
                cls._attitude = {
                    "roll"  : msg_packet["roll"],
                    "pitch" : msg_packet["pitch"],
                    "yaw"   : msg_packet["yaw"],
                    "speed" : {
                        "roll"  : msg_packet["rollspeed"],
                        "pitch" : msg_packet["pitchspeed"],
                        "yaw"   : msg_packet["yawspeed"],
                    },
                    "timestamp" : msg_packet["eb_timestamp"]
                }

            # LOCAL_POSITION_NED
            elif packet_type == "LOCAL_POSITION_NED":
                cls._local_position = {
                    "x"     : msg_packet["x"],
                    "y"     : msg_packet["y"],
                    "z"     : msg_packet["z"],
                    "speed" : {
                        "x": msg_packet["vx"],
                        "y": msg_packet["vy"],
                        "z": msg_packet["vz"]
                    },
                    "timestamp" : msg_packet["eb_timestamp"]
                }

            # GLOBAL_POSITION_INT
            elif packet_type == "GLOBAL_POSITION_INT":
                cls._global_position = {
                    "lat"   : msg_packet["lat"] / (10 ** 7),                 # degree
                    "lon"   : msg_packet["lon"] / (10 ** 7),                 # degree
                    "alt"   : msg_packet["alt"] / (10 ** 3),                 # meters
                    "relative_alt" : msg_packet["relative_alt"] / (10 ** 3), # meters
                    "speed" : {
                        "x": msg_packet["vx"],
                        "y": msg_packet["vy"],
                        "z": msg_packet["vz"]
                    },
                    "yaw" : msg_packet["hdg"],
                    "timestamp" : msg_packet["eb_timestamp"]
                }

            # RC_CHANNELS_RAW
            elif packet_type == "RC_CHANNELS_RAW":
                cls._raw_rc_channels = {
                    "channel_1" : msg_packet["chan1_raw"],
                    "channel_2" : msg_packet["chan2_raw"],
                    "channel_3" : msg_packet["chan3_raw"],
                    "channel_4" : msg_packet["chan4_raw"],
                    "channel_5" : msg_packet["chan5_raw"],
                    "channel_6" : msg_packet["chan6_raw"],
                    "channel_7" : msg_packet["chan7_raw"],
                    "channel_8" : msg_packet["chan8_raw"],
                    "timestamp" : msg_packet["eb_timestamp"]
                }

            # VFR_HUD
            elif packet_type == "VFR_HUD":
                cls._air_speed    = (msg_packet["airspeed"],    msg_packet["eb_timestamp"])
                cls._ground_speed = (msg_packet["groundspeed"], msg_packet["eb_timestamp"])
                cls._heading      = (msg_packet["heading"],     msg_packet["eb_timestamp"])
                cls._throttle     = (msg_packet["throttle"],    msg_packet["eb_timestamp"])
                cls._alt          = (msg_packet["alt"],         msg_packet["eb_timestamp"])
                cls._climb_rate   = (msg_packet["climb"],       msg_packet["eb_timestamp"])

            # COMMAND_ACK
            elif packet_type == "COMMAND_ACK":
                cls._messages["COMMAND_ACK"][msg_packet["command"]] = msg_packet

            if packet_type != "COMMAND_ACK":
                cls._messages[packet_type] = msg_packet

    # Public Method(s)
    def mavlink(self) -> mavutil.mavfile:
        return self._mavlink

    def mav(self) -> any:
        return self._mavlink.mav

    def action(self):
        return self._action

    def telemetry(self):
        return self._telemetry

    def mission(self):
        return self._mission

    def control(self):
        return self._control

    def wait_msg(self, msg, timeout=5000):
        if timeout <= 0:
            raise ValueError("wait_msg() - Timeout is <= 0.")
        elif msg == "COMMAND_ACK":
            raise NotImplementedError

        start_timestamp = Time.get_current_timestamp("ms")

        while 1:
            if msg not in self._messages:
                if Time.get_current_timestamp("ms") - start_timestamp >= timeout:
                    raise TimeoutError("wait_msg() for message {} has timed out."
                                       .format(str(msg)))
                continue

            msg_data = self._messages[msg]

            del self._messages[msg]
            return msg_data

    # type - https://mavlink.io/en/messages/common.html#MAV_RESULT
    def wait_cmd_ack(self, cmd, timeout=5000):
        if timeout <= 0:
            raise ValueError("wait_cmd_ack() - Timeout is <= 0.")

        start_timestamp = Time.get_current_timestamp("ms")

        while 1:
            if cmd not in self._messages["COMMAND_ACK"]:
                if Time.get_current_timestamp("ms") - start_timestamp >= timeout:
                    raise TimeoutError("wait_cmd_ack() for command {} has timed out."
                                       .format(str(cmd)))
                continue

            result = self._messages["COMMAND_ACK"][cmd]["result"]

            del self._messages["COMMAND_ACK"][cmd]
            return result

    # type - https://mavlink.io/en/messages/common.html#MAV_MISSION_RESULT
    def wait_mission_ack(self, timeout=5000):
        if timeout <= 0:
            raise ValueError("wait_mission_ack() - Timeout is <= 0.")

        start_timestamp = Time.get_current_timestamp("ms")

        while 1:
            if "MISSION_ACK" not in self._messages:
                if Time.get_current_timestamp("ms") - start_timestamp >= timeout:
                    raise TimeoutError("wait_mission_ack() timed out.")
                continue

            result = self._messages["MISSION_ACK"]["type"]

            del self._messages["MISSION_ACK"]
            return result

    def set_variable(self, key, val):
        self._variables[key] = val

    def get_variable(self, key):
        if not key in self._variables: return None

        return self._variables[key]

    def get_output_directory(self):
        return self._output_dir
