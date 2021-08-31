"""
         o==[Test Script]==o
   ______________________________
 / \  Globals:                   \.
|   | * drone                    |.
 \_ | * control                  |.
    |                            |.
    |        Description         |.
    | This script will move dr-  |.
    | one for 5.5 meters with    |.
    | the bearing of 70 based on |.
    | compass. After drone reach |.
    | the desired position, it   |.
    | will take 5 photos while   |.
    | holding its position.      |.
    |   _________________________|___
    |  /  Ege Bilecen - 05.09.2020  /.
    \_/____________________________/.
"""
from time import sleep

from eb.camera     import Camera
from eb.logger     import Logger
from eb.drone.math import Math as Drone_Math
import config

camera = Camera(config.Camera.DEVICE_INDEX, file_name  = "flight_vid")
camera.start()
sleep(3)

curr_pos = drone.telemetry().get_global_position()

dest_pos = Drone_Math.calculate_global_position_from_heading_and_distance({"lat" : curr_pos["lat"], "lon" : curr_pos["lon"]},
                                                                          70, 5.5)

control["position"]["hold"]["skip"] = True
sleep(0.5)

Logger.PrintLog("Going to position.")
while 1:
    drone.action().go_to_global_position(dest_pos["lat"], dest_pos["lon"], curr_pos["relative_alt"])
    sleep(0.25)

    res = drone.control().is_reached_to_global_position(dest_pos["lat"], dest_pos["lon"], curr_pos["relative_alt"], 0.15, 0)

    if res: break

control["position"]["hold"]["pos_override"] = {
    "lat" : dest_pos["lat"],
    "lon" : dest_pos["lon"],
    "relative_alt" : curr_pos["relative_alt"]
}
control["position"]["hold"]["skip"] = False
sleep(0.5)

for i in range(5):
    Logger.PrintLog("Saving {}. photo.".format(str(i+1)))
    frame = camera.get_last_frame()

    with open("./photo/"+str(i)+".jpg", "wb") as f:
        f.write(frame)

    sleep(1)

# Custom return
return_val = {
    "it_works" : True
}

Logger.PrintLog("Script execution has ended.")
