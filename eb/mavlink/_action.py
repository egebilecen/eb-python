"""
    Author: Ege Bilecen
    Date  : 15.08.2020
"""
from math import floor
import threading

from eb.logger import Logger
from eb.method import Method
from eb.math   import Math
from eb.time   import Time
import eb.mavlink.helper as eb_mavutil

class Action:
    def __init__(self, vehicle):
        self.LOG_INFO = "_action.py"
        self._vehicle = vehicle

    # Public Method(s)
    def set_flight_mode(self, flight_mode, retries=4, timeout=1500):
        Logger.PrintLog(self.LOG_INFO, "set_flight_mode() - Setting flight mode to {}."
                        .format(flight_mode.upper()))

        flight_mode = flight_mode.upper()
        flight_mode_list = eb_mavutil.get_flight_modes(self._vehicle.mavlink())

        if flight_mode not in flight_mode_list:
            Logger.PrintLog(self.LOG_INFO, "set_flight_mode() - Flight mode {} not in flight mode list."
                            .format(flight_mode))
            return False

        def impl():
            COMMAND = eb_mavutil.Enum.get_int_reference("MAV_CMD_DO_SET_MODE")

            self._vehicle.mav().command_long_send(
                self._vehicle._get_target_system(),
                0,
                COMMAND,
                0,
                # params
                eb_mavutil.Enum.get_int_reference("MAV_MODE_FLAG_CUSTOM_MODE_ENABLED"),
                flight_mode_list[flight_mode],
                0, 0, 0, 0, 0
            )

            res = self._vehicle.wait_cmd_ack(COMMAND, timeout)

            if res == 0:
                Logger.PrintLog(self.LOG_INFO, "set_flight_mode() - Flight mode successfully set to {}."
                                .format(flight_mode))
                return True
            else:
                Logger.PrintLog(self.LOG_INFO, "set_flight_mode() - An error occured while setting flight mode to {}. Result: {}."
                                .format(flight_mode, str(res)))
                return False

        return Method.Repeat.until_value(impl, (), retries, ret_val=True)[0]

    def arm(self, retries=4, timeout=1500):
        Logger.PrintLog(self.LOG_INFO, "arm() - Arming.")

        def impl():
            COMMAND = eb_mavutil.Enum.get_int_reference("MAV_CMD_COMPONENT_ARM_DISARM")

            self._vehicle.mav().command_long_send(
                self._vehicle._get_target_system(),
                self._vehicle._get_target_component(),
                COMMAND,
                0,
                1, 0, 0, 0, 0, 0, 0
            )

            res = self._vehicle.wait_cmd_ack(COMMAND, timeout)

            Logger.PrintLog(self.LOG_INFO, "arm() - Result: {}."
                            .format(str(res)))

            if res == 0: return True
            else:        return False

        if self._vehicle._first_arm:
            first_arm_res = Method.Repeat.until_value(impl, (), retries, ret_val=True)[0]

            if not first_arm_res: return first_arm_res
            else:
                self._vehicle._first_arm = False
                self.arm(retries + 2, timeout)

        return Method.Repeat.until_value(impl, (), retries, ret_val=True)[0]

    def disarm(self, retries=4, timeout=1500):
        Logger.PrintLog(self.LOG_INFO, "disarm() - Disarming.")

        def impl():
            COMMAND = eb_mavutil.Enum.get_int_reference("MAV_CMD_COMPONENT_ARM_DISARM")

            self._vehicle.mav().command_long_send(
                self._vehicle._get_target_system(),
                self._vehicle._get_target_component(),
                COMMAND,
                0,
                0, 0, 0, 0, 0, 0, 0
            )

            res = self._vehicle.wait_cmd_ack(COMMAND, timeout)
            Logger.PrintLog(self.LOG_INFO, "disarm() - Result: {}."
                            .format(str(res)))

            if res == 0:
                return True
            else:
                return False

        return Method.Repeat.until_value(impl, (), retries, ret_val=True)[0]

    # GUIDED mode only.
    # spd - m/s
    def set_air_speed(self, spd, retries=4, timeout=1500):
        Logger.PrintLog(self.LOG_INFO, "set_air_speed() - Setting air speed to {} m/s."
                        .format(str(spd)))

        if self._vehicle.telemetry().get_flight_mode() != "GUIDED":
            Logger.PrintLog(self.LOG_INFO, "set_air_speed() - Cannot set air speed. Vehicle is not in GUIDED mode.")
            return False

        def impl():
            COMMAND = eb_mavutil.Enum.get_int_reference("MAV_CMD_DO_CHANGE_SPEED")

            self._vehicle.mav().command_long_send(
                self._vehicle._get_target_system(),
                self._vehicle._get_target_component(),
                COMMAND,
                0,
                # params
                0, spd, -1, 0, 0, 0, 0
            )

            res = self._vehicle.wait_cmd_ack(COMMAND, timeout)
            Logger.PrintLog(self.LOG_INFO, "set_air_speed() - Result: {}."
                            .format(str(res)))

            if res == 0:
                return True
            else:
                return False

        return Method.Repeat.until_value(impl, (), retries, ret_val=True)[0]

    # GUIDED mode only.
    # spd - m/s
    def set_ground_speed(self, spd, retries=4, timeout=1500):
        Logger.PrintLog(self.LOG_INFO, "set_ground_speed() - Setting ground speed to {} m/s."
                        .format(str(spd)))

        if self._vehicle.telemetry().get_flight_mode() != "GUIDED":
            Logger.PrintLog(self.LOG_INFO, "set_ground_speed() - Cannot set ground speed. Vehicle is not in GUIDED mode.")
            return False

        def impl():
            COMMAND = eb_mavutil.Enum.get_int_reference("MAV_CMD_DO_CHANGE_SPEED")

            self._vehicle.mav().command_long_send(
                self._vehicle._get_target_system(),
                self._vehicle._get_target_component(),
                COMMAND,
                0,
                # params
                1, spd, -1, 0, 0, 0, 0
            )

            res = self._vehicle.wait_cmd_ack(COMMAND, timeout)
            Logger.PrintLog(self.LOG_INFO, "set_ground_speed() - Result: {}."
                            .format(str(res)))

            if res == 0: return True
            else:        return False

        return Method.Repeat.until_value(impl, (), retries, ret_val=True)[0]

    # GUIDED mode only.
    # spd - m/s
    def set_climb_speed(self, spd, retries=4, timeout=1500):
        Logger.PrintLog(self.LOG_INFO, "set_climb_speed() - Setting climb speed to {} m/s."
                        .format(str(spd)))

        if self._vehicle.telemetry().get_flight_mode() != "GUIDED":
            Logger.PrintLog(self.LOG_INFO, "set_climb_speed() - Cannot set climb speed. Vehicle is not in GUIDED mode.")
            return False

        def impl():
            COMMAND = eb_mavutil.Enum.get_int_reference("MAV_CMD_DO_CHANGE_SPEED")

            self._vehicle.mav().command_long_send(
                self._vehicle._get_target_system(),
                self._vehicle._get_target_component(),
                COMMAND,
                0,
                # params
                2, spd, -1, 0, 0, 0, 0
            )

            res = self._vehicle.wait_cmd_ack(COMMAND, timeout)
            Logger.PrintLog(self.LOG_INFO, "set_climb_speed() - Result: {}."
                            .format(str(res)))

            if res == 0: return True
            else:        return False

        return Method.Repeat.until_value(impl, (), retries, ret_val=True)[0]

    # GUIDED mode only.
    # spd - m/s
    def set_descent_speed(self, spd, retries=4, timeout=1500):
        Logger.PrintLog(self.LOG_INFO, "set_descent_speed() - Setting descent speed to {} m/s."
                        .format(str(spd)))

        if self._vehicle.telemetry().get_flight_mode() != "GUIDED":
            Logger.PrintLog(self.LOG_INFO, "set_descent_speed() - Cannot set descent speed. Vehicle is not in GUIDED mode.")
            return False

        def impl():
            COMMAND = eb_mavutil.Enum.get_int_reference("MAV_CMD_DO_CHANGE_SPEED")

            self._vehicle.mav().command_long_send(
                self._vehicle._get_target_system(),
                self._vehicle._get_target_component(),
                COMMAND,
                0,
                # params
                3, spd, -1, 0, 0, 0, 0
            )

            res = self._vehicle.wait_cmd_ack(COMMAND, timeout)
            Logger.PrintLog(self.LOG_INFO, "set_descent_speed() - Result: {}."
                            .format(str(res)))

            if res == 0: return True
            else:        return False

        return Method.Repeat.until_value(impl, (), retries, ret_val=True)[0]

    # GUIDED mode only.
    # deg - degree | spd - m/s
    def set_yaw(self, deg, retries=4, timeout=1500):
        Logger.PrintLog(self.LOG_INFO, "set_yaw() - Setting yaw degree to {}°."
                        .format(str(deg)))

        if self._vehicle.telemetry().get_flight_mode() != "GUIDED":
            Logger.PrintLog(self.LOG_INFO, "set_yaw() - Cannot set yaw degree. Vehicle is not in GUIDED mode.")
            return False

        def impl():
            COMMAND = eb_mavutil.Enum.get_int_reference("MAV_CMD_CONDITION_YAW")

            self._vehicle.mav().command_long_send(
                self._vehicle._get_target_system(),
                self._vehicle._get_target_component(),
                COMMAND,
                0,
                # params
                deg, 0, 0, 0, 0, 0, 0
            )

            res = self._vehicle.wait_cmd_ack(COMMAND, timeout)
            Logger.PrintLog(self.LOG_INFO, "set_yaw() - Result: {}."
                            .format(str(res)))

            if res == 0: return True
            else:        return False

        return Method.Repeat.until_value(impl, (), retries, ret_val=True)[0]

    # GUIDED mode only.
    # vel_x - m/s | vel_y - m/s | vel_z - m/s
    # NED frame reference: https://trello-attachments.s3.amazonaws.com/5dea77afa5dce744336f16d6/643x553/8d87700e0e8e221d87e59fef4e443d18/Body-and-North-East-Down-frames-on-a-quadcopter.png
    def move_based_local_ned(self, vel_x, vel_y, vel_z, duration_ms=500):
        Logger.PrintLog(self.LOG_INFO, "move_based_local_ned() - Moving based on NED. X:{} m/s, Y:{} m/s, Z:{} m/s."
                        .format(str(vel_x), str(vel_y), str(vel_z)))

        if self._vehicle.telemetry().get_flight_mode() != "GUIDED":
            Logger.PrintLog(self.LOG_INFO, "move_based_local_ned() - Cannot move based on NED. Vehicle is not in GUIDED mode.")
            return False

        start_timestamp = Time.get_current_timestamp("ms")

        while 1:
            eb_mavutil.Enum.get_method_reference(self._vehicle.mav(), "SET_POSITION_TARGET_LOCAL_NED")(
                0,
                self._vehicle._get_target_system(),
                self._vehicle._get_target_component(),
                eb_mavutil.Enum.get_int_reference("MAV_FRAME_LOCAL_NED"),
                0b0000111111000111,
                0, 0, 0,
                vel_x, vel_y, vel_z,
                0, 0, 0,
                0, 0
            )

            if duration_ms <= 0 \
            or Time.get_current_timestamp("ms") - start_timestamp >= duration_ms:
                break

        return True

    # GUIDED mode only.
    def go_to_global_position(self, lat, lon, rel_alt):
        Logger.PrintLog(self.LOG_INFO, "go_to_global_position() - Attempting to going to destination global position.")

        if self._vehicle.telemetry().get_flight_mode() != "GUIDED":
            Logger.PrintLog(
                self.LOG_INFO, "go_to_global_position() - Cannot go to destination global position. Vehicle is not in GUIDED mode.")
            return False

        eb_mavutil.Enum.get_method_reference(self._vehicle.mav(), "MISSION_ITEM")(
            self._vehicle._get_target_system(),
            self._vehicle._get_target_component(),
            0,
            eb_mavutil.Enum.get_int_reference("MAV_FRAME_GLOBAL_RELATIVE_ALT"),
            eb_mavutil.Enum.get_int_reference("MAV_CMD_NAV_WAYPOINT"),
            2, 0,
            0, 0, 0, 0,
            lat, lon, rel_alt
        )

        return True

    # GUIDED mode only.
    def go_to_local_position(self, x, y, z):
        Logger.PrintLog(self.LOG_INFO, "go_to_local_position() - Attempting to going to destination local position. X: {}, Y: {}, Z: {}."
                        .format(str(x), str(y), str(z)))

        if self._vehicle.telemetry().get_flight_mode() != "GUIDED":
            Logger.PrintLog(
                self.LOG_INFO, "go_to_local_position() - Cannot go to destination local position. Vehicle is not in GUIDED mode.")
            return False

        eb_mavutil.Enum.get_method_reference(self._vehicle.mav(), "MISSION_ITEM")(
            self._vehicle._get_target_system(),
            self._vehicle._get_target_component(),
            0,
            eb_mavutil.Enum.get_int_reference("MAV_FRAME_LOCAL_NED"),
            eb_mavutil.Enum.get_int_reference("MAV_CMD_NAV_WAYPOINT"),
            2, 0,
            0, 0, 0, 0,
            x, y, z
        )

        return True

    # GUIDED mode only.
    """
        hold_dict - { "hold" : True/False,
                      "current_pos"  : { "lat" : 65.2421, "lon" : 25.3214, "relative_alt" : 10.0 } (will set in below),
                      "skip"         : True/False, (Optional)
                      "pos_override" : { "lat" : 65.2421, "lon" : 25.3214, "relative_alt" : 10.0 } (Optional)
                    }
    """
    def hold_global_position(self, hold_dict, update_interval=250):
        Logger.PrintLog(self.LOG_INFO, "hold_global_position() - Attempting to hold vehicle's global position.")

        if self._vehicle.telemetry().get_flight_mode() != "GUIDED":
            Logger.PrintLog(self.LOG_INFO, "hold_global_position() - Cannot hold vehicle's global position. Vehicle is not in GUIDED mode.")
            return False

        global_pos = self._vehicle.telemetry().get_global_position()

        if global_pos == {}:
            Logger.PrintLog(self.LOG_INFO, "hold_global_position() - Cannot hold vehicle's global position. Global position information is not yet set.")
            return False

        hold_dict["current_pos"] = {
            "lat" : global_pos["lat"],
            "lon" : global_pos["lon"],
            "relative_alt" : global_pos["relative_alt"]
        }

        def impl(cls, hold):
            Logger.PrintLog(cls.LOG_INFO, "hold_global_position() - Handler has started. Lat:{}, Lon:{}, Alt:{}."
                            .format(str(hold["current_pos"]["lat"]), str(hold["current_pos"]["lon"]), str(hold["current_pos"]["relative_alt"])))

            start_timestamp = Time.get_current_timestamp("ms")
            update_counter  = -1

            while hold["hold"] \
            and   self._vehicle.telemetry().get_flight_mode() == "GUIDED":
                if hold.get("skip", False): continue
                if hold.get("pos_override", None) is not None:
                    Logger.PrintLog(cls.LOG_INFO, "hold_global_position() - impl() - Position override detected. Current lat: {}, lon:{}, relative alt:{}. Overridden lat: {}, lon: {}, relative alt: {}."
                                    .format(str(hold["current_pos"]["lat"]), str(hold["current_pos"]["lon"]), str(hold["current_pos"]["relative_alt"]),
                                            str(hold["pos_override"]["lat"]), str(hold["pos_override"]["lon"]), str(hold["pos_override"]["relative_alt"])))

                    hold["current_pos"]  = hold["pos_override"]
                    hold["pos_override"] = None

                if floor((Time.get_current_timestamp("ms") - start_timestamp) / update_interval) > update_counter:
                    COMMAND = eb_mavutil.Enum.get_int_reference("MAV_CMD_NAV_WAYPOINT")

                    eb_mavutil.Enum.get_method_reference(self._vehicle.mav(), "MISSION_ITEM")(
                        self._vehicle._get_target_system(),
                        self._vehicle._get_target_component(),
                        0,
                        eb_mavutil.Enum.get_int_reference("MAV_FRAME_GLOBAL_RELATIVE_ALT"),
                        COMMAND,
                        2, 0,
                        0, 0, 0, 0,
                        hold["current_pos"]["lat"], hold["current_pos"]["lon"], hold["current_pos"]["relative_alt"]
                    )

                    update_counter += 1

            hold["ended"] = True

            Logger.PrintLog(self.LOG_INFO, "hold_global_position() - Handler has ended.")

        _ = threading.Thread(target=impl, args=(self, hold_dict))
        _.daemon = False
        _.start()

    # GUIDED mode only.
    """
        hold_dict - { "hold" : True/False,
                      "current_pos"  : { "x" : 1.2421, "y" : 0.3214, "z" : 10.0 } (will set in below),
                      "skip"         : True/False, (Optional)
                      "pos_override" : { "x" : 1.2421, "y" : 0.3214, "z" : 10.0 } (Optional)
                    }
    """
    def hold_local_position(self, hold_dict, update_interval=250):
        Logger.PrintLog(self.LOG_INFO, "hold_local_position() - Attempting to hold vehicle's local position.")

        if self._vehicle.telemetry().get_flight_mode() != "GUIDED":
            Logger.PrintLog(self.LOG_INFO, "hold_local_position() - Cannot hold vehicle's local position. Vehicle is not in GUIDED mode.")
            return False

        local_pos = self._vehicle.telemetry().get_local_position()

        hold_dict["current_pos"] = {
            "x" : local_pos["x"],
            "y" : local_pos["y"],
            "z" : local_pos["z"]
        }

        if local_pos == {}:
            Logger.PrintLog(self.LOG_INFO, "hold_local_position() - Cannot hold vehicle's local position. Local position information is not yet set.")
            return False

        def impl(cls, hold):
            Logger.PrintLog(cls.LOG_INFO, "hold_local_position() - Handler has started. X:{}, Y:{}, Z:{}."
                            .format(str(hold["current_pos"]["x"]), str(hold["current_pos"]["y"]), str(hold["current_pos"]["z"])))

            start_timestamp = Time.get_current_timestamp("ms")
            update_counter  = -1

            while hold["hold"]:
                if hold.get("skip", False): continue
                if hold.get("pos_override", None) is not None:
                    Logger.PrintLog(cls.LOG_INFO, "hold_local_position() - impl() - Position override detected. Current X: {}, Y:{}, Z:{}. Overridden X: {}, Y: {}, Z: {}."
                                    .format(str(hold["current_pos"]["x"]), str(hold["current_pos"]["y"]), str(hold["current_pos"]["z"]),
                                            str(hold["pos_override"]["x"]), str(hold["pos_override"]["y"]), str(hold["pos_override"]["z"])))

                    hold["current_pos"]  = hold["pos_override"]
                    hold["pos_override"] = None

                if floor((Time.get_current_timestamp("ms") - start_timestamp) / update_interval) > update_counter:
                    COMMAND = eb_mavutil.Enum.get_int_reference("MAV_CMD_NAV_WAYPOINT")

                    eb_mavutil.Enum.get_method_reference(self._vehicle.mav(), "MISSION_ITEM")(
                        self._vehicle._get_target_system(),
                        self._vehicle._get_target_component(),
                        0,
                        eb_mavutil.Enum.get_int_reference("MAV_FRAME_LOCAL_NED"),
                        COMMAND,
                        2, 0,
                        0, 0, 0, 0,
                        hold["current_pos"]["x"], hold["current_pos"]["y"], hold["current_pos"]["z"]
                    )

                    update_counter += 1

            hold["ended"] = True

            Logger.PrintLog(self.LOG_INFO, "hold_local_position() - Handler has ended.")

        _ = threading.Thread(target=impl, args=(self, hold_dict))
        _.daemon = False
        _.start()

    # GUIDED mode only.
    def takeoff(self, rel_alt, retries=12, timeout=500):
        Logger.PrintLog(self.LOG_INFO, "takeoff() - Attempting to taking off to altitude: {} m."
                        .format(str(rel_alt)))

        if self._vehicle.telemetry().get_flight_mode() != "GUIDED":
            Logger.PrintLog(self.LOG_INFO, "takeoff() - Cannot takeoff. Vehicle is not in GUIDED mode.")
            return False

        def impl():
            COMMAND = eb_mavutil.Enum.get_int_reference("MAV_CMD_NAV_TAKEOFF")

            self._vehicle.mav().command_long_send(
                self._vehicle._get_target_system(),
                self._vehicle._get_target_component(),
                COMMAND,
                0,
                # params
                0, 0, 0, 0,
                0, 0, rel_alt
            )

            res = self._vehicle.wait_cmd_ack(COMMAND, timeout)
            Logger.PrintLog(self.LOG_INFO, "takeoff() - Result: {}."
                            .format(str(res)))

            if res == 0:
                return True
            else:
                return False

        return Method.Repeat.until_value(impl, (), retries, ret_val=True)[0]

    # GUIDED mode only.
    def land(self, retries=12, timeout=500):
        Logger.PrintLog(self.LOG_INFO, "land() - Attempting to land.")

        if self._vehicle.telemetry().get_flight_mode() != "GUIDED":
            Logger.PrintLog(self.LOG_INFO, "land() - Cannot land. Vehicle is not in GUIDED mode.")
            return False

        def impl():
            COMMAND = eb_mavutil.Enum.get_int_reference("MAV_CMD_NAV_LAND")

            self._vehicle.mav().command_long_send(
                self._vehicle._get_target_system(),
                self._vehicle._get_target_component(),
                COMMAND,
                0,
                # params
                0, 0, 0, 0,
                0, 0, 0
            )

            res = self._vehicle.wait_cmd_ack(COMMAND, timeout)
            Logger.PrintLog(self.LOG_INFO, "land() - Result: {}."
                            .format(str(res)))

            if res == 0:
                return True
            else:
                return False

        return Method.Repeat.until_value(impl, (), retries, ret_val=True)[0]

    # GUIDED mode only.
    def set_home_position(self, retries=12, timeout=500):
        Logger.PrintLog(self.LOG_INFO, "set_home_position() - Attempting to set home position.")

        if self._vehicle.telemetry().get_flight_mode() != "GUIDED":
            Logger.PrintLog(self.LOG_INFO, "set_home_position() - Cannot set home position. Vehicle is not in GUIDED mode.")
            return False

        def impl():
            COMMAND = eb_mavutil.Enum.get_int_reference("MAV_CMD_DO_SET_HOME")

            self._vehicle.mav().command_long_send(
                self._vehicle._get_target_system(),
                self._vehicle._get_target_component(),
                COMMAND,
                0,
                # params
                1, 0, 0, 0, 0, 0, 0
            )

            res = self._vehicle.wait_cmd_ack(COMMAND, timeout)
            Logger.PrintLog(self.LOG_INFO, "set_home_position() - Result: {}."
                            .format(str(res)))

            if res == 0:
                return True
            else:
                return False

        return Method.Repeat.until_value(impl, (), retries, ret_val=True)[0]

    """
        Main Out 1 - Servo Channel: 1
        Main Out 2 - Servo Channel: 2
        Main Out 3 - Servo Channel: 3
        Main Out 4 - Servo Channel: 4
        Main Out 5 - Servo Channel: 5
        Main Out 6 - Servo Channel: 6
        Main Out 7 - Servo Channel: 7
        Main Out 8 - Servo Channel: 8
        Aux  Out 1 - Servo Channel: 9
        Aux  Out 2 - Servo Channel: 10
        Aux  Out 3 - Servo Channel: 11
        Aux  Out 4 - Servo Channel: 12
        Aux  Out 5 - Servo Channel: 13
        Aux  Out 6 - Servo Channel: 14
    """
    def set_servo_pwm(self, channel, pwm, retries=12, timeout=500):
        Logger.PrintLog(self.LOG_INFO, "set_servo_pwm() - Setting servo's pwm at channel {} to {}."
                        .format(str(channel), str(pwm)))

        def impl():
            COMMAND = eb_mavutil.Enum.get_int_reference("MAV_CMD_DO_SET_SERVO")

            self._vehicle.mav().command_long_send(
                self._vehicle._get_target_system(),
                self._vehicle._get_target_component(),
                COMMAND,
                0,
                # params
                channel, pwm, 0, 0, 0, 0, 0
            )

            res = self._vehicle.wait_cmd_ack(COMMAND, timeout)
            Logger.PrintLog(self.LOG_INFO, "set_servo_pwm() - Result: {}."
                            .format(str(res)))

            if res == 0:
                return True
            else:
                return False

        return Method.Repeat.until_value(impl, (), retries, ret_val=True)[0]

    def set_relay(self, channel, status, retries=12, timeout=500):
        Logger.PrintLog(self.LOG_INFO, "set_relay() - Setting relay's status at channel {} to {}."
                        .format(str(channel), str(status)))

        if  status != 0 \
        and status != 1: raise ValueError("Status must be either 0 or 1.")

        def impl():
            COMMAND = eb_mavutil.Enum.get_int_reference("MAV_CMD_DO_SET_RELAY")

            self._vehicle.mav().command_long_send(
                self._vehicle._get_target_system(),
                self._vehicle._get_target_component(),
                COMMAND,
                0,
                # params
                channel, status, 0, 0, 0, 0, 0
            )

            res = self._vehicle.wait_cmd_ack(COMMAND, timeout)
            Logger.PrintLog(self.LOG_INFO, "set_relay() - Result: {}."
                            .format(str(res)))

            if res == 0:
                return True
            else:
                return False

        return Method.Repeat.until_value(impl, (), retries, ret_val=True)[0]

    def rc_channel_override(self, channel, val_or_percentage, use_val=True, min_ppm_us=1000, max_ppm_us=2000):
        CHANNEL_COUNT = 8
        
        if channel < 1 \
        or channel > CHANNEL_COUNT:
            raise ValueError("Channel must be between 1 and {}. (inclusive)".format(str(CHANNEL_COUNT)))
        
        write_val = 0

        if val_or_percentage != 0:
            if use_val:
                if  val_or_percentage < min_ppm_us:
                    raise ValueError("PPM us value cannot be less than min_ppm_us.")
                
                if val_or_percentage > max_ppm_us:
                    raise ValueError("PPM us value cannot be less than max_ppm_us.")

                write_val = val_or_percentage
            else: 
                if val_or_percentage < 1 \
                or val_or_percentage > 100:
                    raise ValueError("Percentage must be between 1 and 100. (inclusive)")

                write_val = Math.Value.map(val_or_percentage, 1, 100, min_ppm_us, max_ppm_us)
        
        UINT16_MAX = 65535
        raw_channel_values = [UINT16_MAX for _ in range(CHANNEL_COUNT)]
        raw_channel_values[channel - 1] = write_val

        eb_mavutil.Enum.get_method_reference(self._vehicle.mav(), "RC_CHANNELS_OVERRIDE")(
            self._vehicle._get_target_system(),
            self._vehicle._get_target_component(),
            *raw_channel_values
        )

        return True
