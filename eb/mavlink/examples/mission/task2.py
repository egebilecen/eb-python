"""
        o==[Task 2 Script]==o
   ______________________________
 / \  Globals:                   \.
|   | * vehicle                  |.
 \_ | * control                  |.
    |   _________________________|___
    |  /  Ege Bilecen - 09.09.2020  /.
    \_/____________________________/.
    
    This script was written for TÜBİTAK International Unmanned Aerial Vehicles Competition 2020.
    I am just sharing this script to show how action methods are used to guide the drone. You can
    either choose to setting "skip" in control["position"]["hold"] to True and guide the drone
    using drone.action().go_to_global_position() (this is the same guidance way used in go_to_gps_coord.py)
    or simply override GPS coordinates in control["position"]["hold"] and drone will go to that
    coordinates which is the way that used in this script.
"""
from time import sleep

from eb.logger       import Logger
from eb.compass      import Compass
from eb.method       import Method
from eb.time         import Time
from eb.mavlink.math import Math as VehicleMath
from eb.image_processing.util import Util

import config
import func

# Defines
LOG_INFO = "[MISSION_SCRIPT] - task2.py - "

POLE_COMPASS_BEARING         = config.Drone.Task.Two.POLE_COMPASS_BEARING
POLE_COMPASS_COUNTER_BEARING = Compass.get_counter_heading(POLE_COMPASS_BEARING)
POLE_1_COORDS                = config.Drone.Task.Two.POLE_1_COORDS
POLE_1_COUNTER_COORDS        = config.Drone.Task.Two.POLE_1_COUNTER_COORDS
POLE_2_COORDS                = config.Drone.Task.Two.POLE_2_COORDS
POLE_2_COUNTER_COORDS        = config.Drone.Task.Two.POLE_2_COUNTER_COORDS
WATER_PICKUP_POOL_COORDS     = config.Drone.Task.Two.WATER_PICKUP_POOL_COORDS
HEADING_THRESHOLD            = config.Drone.Task.Two.HEADING_THRESHOLD
WATER_PICKUP_LINE_COORDS     = config.Drone.Task.Two.WATER_PICKUP_LINE_COORDS

HOME_POSITION         = vehicle.get_variable("eb_home_pos")
LAND_POSITION         = config.Drone.Task.Two.LAND_POSITION

FLIGHT_ALTITUDE       = config.Drone.Task.Two.FLIGHT_ALTITUDE
MISSION_ALTITUDE      = config.Drone.Task.Two.MISSION_ALTITUDE
WATER_PICKUP_ALTITUDE = config.Drone.Task.Two.WATER_PICKUP_ALTITUDE
WATER_DROP_ALTITUDE   = config.Drone.Task.Two.WATER_DROP_ALTITUDE
ALTITUDE_THRESHOLD    = config.Drone.Task.Two.ALTITUDE_THRESHOLD

# Variables
dist_sensor = vehicle.get_variable("dist_sensor")
camera      = vehicle.get_variable("camera")
first_tour_completed = False

while 1:
    try:
        if vehicle.mission().get_status() != 1:
            Logger.PrintLog(LOG_INFO + "Mission status is not 1. Aborting...")
            break
        elif vehicle.telemetry().get_flight_mode() != "GUIDED":
            Logger.PrintLog(LOG_INFO + "Flight mode is not GUIDED. Aborting...")
            break

        # Go to Pole 2's alignment
        Logger.PrintLog(LOG_INFO + "Going to Pole 2's alignment.")

        dest_pos = {"lat" : POLE_2_COUNTER_COORDS[0], "lon" : POLE_2_COUNTER_COORDS[1]} 
        dest_alt = FLIGHT_ALTITUDE

        control["position"]["hold"]["pos_override"] = {
            "lat" : dest_pos["lat"],
            "lon" : dest_pos["lon"],
            "relative_alt" : dest_alt
        }

        Method.Wait.until_value(vehicle.control().is_reached_to_global_position,
                                (dest_pos["lat"], dest_pos["lon"], dest_alt, 0.45, 0),
                                0, 250, ret_val=True)

        Logger.PrintLog(LOG_INFO + "Reached to Pole 2's alignment. Going for 5 meters in 45 degree heading.")

        # Do fake circle toward right
        current_pos = vehicle.telemetry().get_global_position()
        dest_pos    = VehicleMath.calculate_global_position_from_heading_and_distance({"lat" : current_pos["lat"], "lon" : current_pos["lon"]},
                                                                                     Compass.add_to_heading(POLE_COMPASS_BEARING, 30),
                                                                                     15)
        dest_alt    = FLIGHT_ALTITUDE

        control["position"]["hold"]["pos_override"] = {
            "lat" : dest_pos["lat"],
            "lon" : dest_pos["lon"],
            "relative_alt" : dest_alt
        }

        Method.Wait.until_value(vehicle.control().is_reached_to_global_position,
                                (dest_pos["lat"], dest_pos["lon"], dest_alt, 0.45, 0),
                                0, 250, ret_val=True)

        # Go to Pole 2
        Logger.PrintLog(LOG_INFO + "Going to in front of Pole 2.")

        dest_pos = VehicleMath.calculate_global_position_from_heading_and_distance({"lat" : POLE_2_COORDS[0], "lon" : POLE_2_COORDS[1]},
                                                                                  POLE_COMPASS_COUNTER_BEARING,
                                                                                  5)
        dest_alt = FLIGHT_ALTITUDE

        control["position"]["hold"]["pos_override"] = {
            "lat" : dest_pos["lat"],
            "lon" : dest_pos["lon"],
            "relative_alt" : dest_alt
        }

        Method.Wait.until_value(vehicle.control().is_reached_to_global_position,
                                (dest_pos["lat"], dest_pos["lon"], dest_alt, 0.45, 0),
                                0, 250, ret_val=True)

        if first_tour_completed:
            bg_exec_status = Method.execute_in_background(func.lower_water_pump, (vehicle,))

            # Go to water pickup pool coords
            dest_pos = {"lat" : WATER_PICKUP_POOL_COORDS[0], "lon" : WATER_PICKUP_POOL_COORDS[1]}
            dest_alt = FLIGHT_ALTITUDE

            control["position"]["hold"]["pos_override"] = {
                "lat" : dest_pos["lat"],
                "lon" : dest_pos["lon"],
                "relative_alt" : dest_alt
            }

            Method.Wait.until_value(vehicle.control().is_reached_to_global_position,
                                    (dest_pos["lat"], dest_pos["lon"], dest_alt, 0.45, 0),
                                    0, 250, ret_val=True)

            dest_alt = FLIGHT_ALTITUDE - 2.5

            control["position"]["hold"]["pos_override"] = {
                "lat" : dest_pos["lat"],
                "lon" : dest_pos["lon"],
                "relative_alt" : dest_alt
            }

            Method.Wait.until_value(vehicle.control().is_reached_to_global_position,
                                    (dest_pos["lat"], dest_pos["lon"], dest_alt, 0.45, 0),
                                    0, 250, ret_val=True)

            dest_alt = FLIGHT_ALTITUDE - 5

            control["position"]["hold"]["pos_override"] = {
                "lat" : dest_pos["lat"],
                "lon" : dest_pos["lon"],
                "relative_alt" : dest_alt
            }

            Method.Wait.until_value(vehicle.control().is_reached_to_global_position,
                                    (dest_pos["lat"], dest_pos["lon"], dest_alt, 0.45, 0),
                                    0, 250, ret_val=True)

            dest_alt = FLIGHT_ALTITUDE - 7.5

            control["position"]["hold"]["pos_override"] = {
                "lat" : dest_pos["lat"],
                "lon" : dest_pos["lon"],
                "relative_alt" : dest_alt
            }

            Method.Wait.until_value(vehicle.control().is_reached_to_global_position,
                                    (dest_pos["lat"], dest_pos["lon"], dest_alt, 0.45, 0),
                                    0, 250, ret_val=True)

            dest_alt = 1.5

            control["position"]["hold"]["pos_override"] = {
                "lat" : dest_pos["lat"],
                "lon" : dest_pos["lon"],
                "relative_alt" : dest_alt
            }

            Method.Wait.until_value(vehicle.control().is_reached_to_global_position,
                                    (dest_pos["lat"], dest_pos["lon"], dest_alt, 0.45, 0),
                                    0, 250, ret_val=True)

            dest_alt = WATER_PICKUP_ALTITUDE

            control["position"]["hold"]["pos_override"] = {
                "lat" : dest_pos["lat"],
                "lon" : dest_pos["lon"],
                "relative_alt" : dest_alt
            }

            Method.Wait.until_value(vehicle.control().is_reached_to_global_position,
                                    (dest_pos["lat"], dest_pos["lon"], dest_alt, 0.45, 0),
                                    0, 250, ret_val=True)

            Method.Dict.wait_until_value(bg_exec_status,
                                         "completed",
                                         True)

            # start pump
            func.toggle_water_pump(vehicle)
            sleep(config.Drone.Motor.Servo.WATER_TANK.FILL_TIME)

            # stop pump
            func.toggle_water_pump(vehicle)

            Method.execute_in_background(func.raise_water_pump, (vehicle,))

            dest_alt = FLIGHT_ALTITUDE

            control["position"]["hold"]["pos_override"] = {
                "lat" : dest_pos["lat"],
                "lon" : dest_pos["lon"],
                "relative_alt" : dest_alt
            }

            Method.Wait.until_value(vehicle.control().is_reached_to_global_position,
                                    (dest_pos["lat"], dest_pos["lon"], dest_alt, 0.45, 0),
                                    0, 250, ret_val=True)

            dest_pos = {"lat" : WATER_PICKUP_LINE_COORDS[0], "lon" : WATER_PICKUP_LINE_COORDS[1]}
            dest_alt = FLIGHT_ALTITUDE

            control["position"]["hold"]["pos_override"] = {
                "lat": dest_pos["lat"],
                "lon": dest_pos["lon"],
                "relative_alt": dest_alt
            }

            Method.Wait.until_value(vehicle.control().is_reached_to_global_position,
                                    (dest_pos["lat"], dest_pos["lon"], dest_alt, 0.45, 0),
                                    0, 250, ret_val=True)

            # Go to water drop area
            detected_once = False
            detection_timestamp = None

            while vehicle.telemetry().get_flight_mode() == "GUIDED":
                heading_left = Compass.substract_from_heading(POLE_COMPASS_BEARING, 90)
                current_pos  = vehicle.telemetry().get_global_position()

                if not detected_once:
                    dest_pos = VehicleMath.calculate_global_position_from_heading_and_distance({"lat" : current_pos["lat"], "lon" : current_pos["lon"]},
                                                                                              heading_left,
                                                                                              2.5)

                    dest_alt = FLIGHT_ALTITUDE

                    control["position"]["hold"]["pos_override"] = {
                        "lat" : dest_pos["lat"],
                        "lon" : dest_pos["lon"],
                        "relative_alt" : dest_alt
                    }

                    Method.Wait.until_value(vehicle.control().is_reached_to_global_position,
                                            (dest_pos["lat"], dest_pos["lon"], dest_alt, 0.45, 0),
                                            0, 250, ret_val=True)

                    sleep(0.5)
                elif detection_timestamp is None:
                    detection_timestamp = Time.get_current_timestamp("ms")
                elif detection_timestamp is not None \
                and  Time.get_current_timestamp("ms") - detection_timestamp >= 15000:
                    func.open_water_tank(vehicle)
                    sleep(5)

                    dest_alt = FLIGHT_ALTITUDE

                    control["position"]["hold"]["pos_override"] = {
                        "lat" : control["position"]["hold"]["current_pos"]["lat"],
                        "lon" : control["position"]["hold"]["current_pos"]["lon"],
                        "relative_alt" : dest_alt
                    }

                    Method.Wait.until_value(vehicle.control().is_reached_to_global_position,
                                            (dest_pos["lat"], dest_pos["lon"], dest_alt, 0.45, 0),
                                            0, 250, ret_val=True)

                    break

                detection_list = vehicle.get_variable("ip_circle_list")

                if detection_list is None \
                or not detection_list[0]:
                    if current_pos["relative_alt"] <= MISSION_ALTITUDE + ALTITUDE_THRESHOLD:
                        dest_alt = WATER_DROP_ALTITUDE

                        control["position"]["hold"]["pos_override"] = {
                            "lat" : control["position"]["hold"]["current_pos"]["lat"],
                            "lon" : control["position"]["hold"]["current_pos"]["lon"],
                            "relative_alt" : dest_alt
                        }

                        Method.Wait.until_value(vehicle.control().is_reached_to_global_position,
                                                (dest_pos["lat"], dest_pos["lon"], dest_alt, 0.45, 0),
                                                0, 250, ret_val=True)

                        func.open_water_tank(vehicle)
                        sleep(5)

                        dest_alt = FLIGHT_ALTITUDE

                        control["position"]["hold"]["pos_override"] = {
                            "lat" : control["position"]["hold"]["current_pos"]["lat"],
                            "lon" : control["position"]["hold"]["current_pos"]["lon"],
                            "relative_alt" : dest_alt
                        }

                        Method.Wait.until_value(vehicle.control().is_reached_to_global_position,
                                                (dest_pos["lat"], dest_pos["lon"], dest_alt, 0.45, 0),
                                                0, 250, ret_val=True)

                        break
                    else: continue

                detected_once = True

                detected_circle_list = detection_list[0]

                Logger.PrintLog(LOG_INFO + "{} circle(s) detected."
                        .format(str(len(detected_circle_list))))

                nearest_circle = Util.Point.get_closer_point_to_center(detected_circle_list)

                Logger.PrintLog(LOG_INFO + "({}, {}) selected as most nearest point to center."
                                .format(str(nearest_circle[0]), str(nearest_circle[1])))

                point_information = Util.Point.extract_information(nearest_circle)

                global_heading    = vehicle.control().calculate_global_heading_from_relative_heading(point_information[1])

                Logger.PrintLog(LOG_INFO + "Information of selected point, distance: {}, relative heading: {}, global heading: {}"
                                .format(str(point_information[0]), str(point_information[1]), str(global_heading)))

                dest_alt = None

                if point_information[0] > config.Drone.ImageProcessing.DETECTION_RANGE_CIRCLE_RADIUS:
                    Logger.PrintLog(LOG_INFO + "Circle is out of detection range. Moving toward it.")

                    current_pos = vehicle.telemetry().get_global_position()
                    dest_pos    = VehicleMath.calculate_global_position_from_heading_and_distance({"lat" : current_pos["lat"], "lon" : current_pos["lon"]},
                                                                                                 global_heading, 0.50)
                    dest_alt = control["position"]["hold"]["current_pos"]["relative_alt"]

                    control["position"]["hold"]["pos_override"] = {
                        "lat" : dest_pos["lat"],
                        "lon" : dest_pos["lon"],
                        "relative_alt" : dest_alt
                    }

                    Method.Wait.until_value(vehicle.control().is_reached_to_global_position,
                                            (dest_pos["lat"], dest_pos["lon"], dest_alt,
                                             0.45, 0),
                                            0, 250, ret_val=True)
                else:
                    dest_alt = control["position"]["hold"]["current_pos"]["relative_alt"]

                    if dest_alt - 1 >= 3.0 - ALTITUDE_THRESHOLD:
                        dest_alt -= 1
                    else:
                        dest_alt = WATER_DROP_ALTITUDE

                    control["position"]["hold"]["pos_override"] = {
                        "lat" : control["position"]["hold"]["current_pos"]["lat"],
                        "lon" : control["position"]["hold"]["current_pos"]["lon"],
                        "relative_alt" : dest_alt
                    }

                    Method.Wait.until_value(vehicle.control().is_reached_to_global_position,
                                            (dest_pos["lat"], dest_pos["lon"], dest_alt, 0.45, 0),
                                            0, 250, ret_val=True)

                if dest_alt == WATER_DROP_ALTITUDE:
                    func.open_water_tank(vehicle)
                    sleep(5)

                    dest_alt = FLIGHT_ALTITUDE

                    control["position"]["hold"]["pos_override"] = {
                        "lat" : control["position"]["hold"]["current_pos"]["lat"],
                        "lon" : control["position"]["hold"]["current_pos"]["lon"],
                        "relative_alt" : dest_alt
                    }

                    Method.Wait.until_value(vehicle.control().is_reached_to_global_position,
                                            (dest_pos["lat"], dest_pos["lon"], dest_alt, 0.45, 0),
                                            0, 250, ret_val=True)

                    break

        # Go to Pole 1
        Logger.PrintLog(LOG_INFO + "Going to in front of Pole 1.")

        dest_pos    = VehicleMath.calculate_global_position_from_heading_and_distance({"lat" : POLE_1_COORDS[0], "lon" : POLE_1_COORDS[1]},
                                                                                     POLE_COMPASS_COUNTER_BEARING,
                                                                                     7.5)
        dest_alt    = FLIGHT_ALTITUDE

        control["position"]["hold"]["pos_override"] = {
            "lat" : dest_pos["lat"],
            "lon" : dest_pos["lon"],
            "relative_alt" : dest_alt
        }

        Method.Wait.until_value(vehicle.control().is_reached_to_global_position,
                                (dest_pos["lat"], dest_pos["lon"], dest_alt, 0.45, 0),
                                0, 250, ret_val=True)

        # Do fake circle toward left
        current_pos = vehicle.telemetry().get_global_position()
        dest_pos    = VehicleMath.calculate_global_position_from_heading_and_distance({"lat" : current_pos["lat"], "lon" : current_pos["lon"]},
                                                                                     Compass.add_to_heading(POLE_COMPASS_COUNTER_BEARING, 45),
                                                                                     10)

        dest_alt = FLIGHT_ALTITUDE

        control["position"]["hold"]["pos_override"] = {
            "lat" : dest_pos["lat"],
            "lon" : dest_pos["lon"],
            "relative_alt" : dest_alt
        }

        Method.Wait.until_value(vehicle.control().is_reached_to_global_position,
                                (dest_pos["lat"], dest_pos["lon"], dest_alt, 0.45, 0),
                                0, 250, ret_val=True)

        # Go to Pole 1's alignment
        Logger.PrintLog(LOG_INFO + "Going to Pole 1's alignment.")

        dest_pos = {"lat" : POLE_1_COUNTER_COORDS[0], "lon" : POLE_1_COUNTER_COORDS[1]} 
        dest_alt = FLIGHT_ALTITUDE

        control["position"]["hold"]["pos_override"] = {
            "lat" : dest_pos["lat"],
            "lon" : dest_pos["lon"],
            "relative_alt" : dest_alt
        }

        Method.Wait.until_value(vehicle.control().is_reached_to_global_position,
                                (dest_pos["lat"], dest_pos["lon"], dest_alt, 0.45, 0),
                                0, 250, ret_val=True)

        # Go to home position
        Logger.PrintLog(LOG_INFO + "Going to home position.")

        dest_pos = {"lat" : HOME_POSITION[0], "lon" : HOME_POSITION[1]}

        dest_alt = FLIGHT_ALTITUDE

        control["position"]["hold"]["pos_override"] = {
            "lat" : dest_pos["lat"],
            "lon" : dest_pos["lon"],
            "relative_alt" : dest_alt
        }

        Method.Wait.until_value(vehicle.control().is_reached_to_global_position,
                                (dest_pos["lat"], dest_pos["lon"], dest_alt, 0.45, 0),
                                0, 250, ret_val=True)

        if not first_tour_completed:
            first_tour_completed = True
        else:
            dest_pos    = {"lat" : LAND_POSITION[0], "lon" : LAND_POSITION[1]}
            dest_alt    = FLIGHT_ALTITUDE - 5

            control["position"]["hold"]["pos_override"] = {
                "lat" : dest_pos["lat"],
                "lon" : dest_pos["lon"],
                "relative_alt" : dest_alt
            }

            Method.Wait.until_value(vehicle.control().is_reached_to_global_position,
                                    (dest_pos["lat"], dest_pos["lon"], dest_alt, 0.45, 0),
                                    0, 250, ret_val=True)

            # All missions are finished. Land
            Logger.PrintLog(LOG_INFO + "Reached to start point. Landing... Well, hopefully.")
            break

    except Exception as ex:
        Logger.PrintException(LOG_INFO, ex)
        break

return_val = {
    "success" : True
}

Logger.PrintLog("Task 2 script has ended.")
