"""
    Intializes the drone, changes it's flight mode and prints various telemetry data to
    console every one second.
"""

from time import sleep

from eb.drone.drone import Drone
import eb.drone.mavlink_helper as eb_mavutil

drone = Drone("/dev/ttyTHS1",
              115200,
              timeout              = 10000,
              scripts_dir          = "./epl_scripts/",
              mission_control_rate = 4)

drone.action().set_flight_mode("LOITER")

while 1:
    print(drone.telemetry().get_state())
    print(drone.telemetry().get_raw_gps())
    print(drone.telemetry().get_global_position())
    print(drone.telemetry().get_local_position())
    sleep(1)

