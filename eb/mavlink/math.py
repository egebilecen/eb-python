"""
    Author: Ege Bilecen
    Date  : 21.08.2020
"""
import math

class Math:
    EARTH_RADIUS = 6371 * (10 ** 3) # m

    # pos1, pos2 = {"lat" : 25.32231 (degree), "lon" : 22.3421 (degree)}
    @staticmethod
    def calculate_global_position_distance(pos1, pos2):
        pos1_radian = {
            "lat" : math.radians(pos1["lat"]),
            "lon" : math.radians(pos1["lon"])
        }

        pos2_radian = {
            "lat" : math.radians(pos2["lat"]),
            "lon" : math.radians(pos2["lon"])
        }

        return Math.EARTH_RADIUS * math.acos(
                                    (math.sin(pos1_radian["lat"])  * math.sin(pos2_radian["lat"]))
                                    + math.cos(pos1_radian["lat"]) * math.cos(pos2_radian["lat"])
                                    * math.cos(pos2_radian["lon"] - pos1_radian["lon"])
                                   )

    # pos = {"lat" : 25.32231 (degree), "lon" : 22.3421 (degree)}
    # heading  - degree
    # distance - meter
    @staticmethod
    def calculate_global_position_from_heading_and_distance(pos, heading, distance):
        dest_lat = math.asin((math.sin(math.pi / 180 * pos["lat"]) * math.cos(distance / Math.EARTH_RADIUS))
                             + (math.cos(math.pi / 180 * pos["lat"]) * math.sin(distance / Math.EARTH_RADIUS) * math.cos(math.pi / 180 * heading)))

        dest_lon = (math.pi / 180 * pos["lon"]) + (math.atan2(math.sin(math.pi / 180 * heading)
                                                                   * math.sin(distance / Math.EARTH_RADIUS)
                                                                   * math.cos(math.pi / 180 * pos["lat"]),
                                                              math.cos(distance / Math.EARTH_RADIUS)
                                                                   - (math.sin(math.pi / 180 * pos["lat"])
                                                                        * math.sin(dest_lat))))

        return {
            "lat" : dest_lat * 180 / math.pi,
            "lon" : dest_lon * 180 / math.pi
        }

    # pos = {"x" : 1.2314 (meters), "y" : -0.52321 (meters)}
    # heading  - degree
    # distance - meter
    @staticmethod
    def calculate_local_position_from_heading_and_distance(pos, heading, distance):
        dest_x = pos["x"] + (distance * math.cos(heading))
        dest_y = pos["y"] + (distance * math.sin(heading))

        return {
            "x" : dest_x,
            "y" : dest_y
        }

    # pos1, pos2 = {"lat" : 25.32231 (degree), "lon" : 22.3421 (degree)}
    @staticmethod
    def get_relative_heading_between_two_global_position(pos1, pos2):
        dL = pos2["lon"] - pos1["lon"]
        x  = math.cos(pos2["lat"]) * math.sin(dL)
        y  = math.cos(pos1["lat"]) * math.sin(pos2["lat"]) - math.sin(pos1["lat"]) * math.cos(pos2["lat"]) * math.cos(dL)

        bearing = math.degrees(math.atan2(x, y))

        return (bearing + 360) % 360
