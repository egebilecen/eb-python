"""
    Author: Ege Bilecen
    Date  : 04.09.2020
"""
from eb.logger     import Logger
from eb.math       import Math as EB_Math
from eb.drone.math import Math

class Control:
    def __init__(self,
                 drone):
        self.LOG_INFO = "control.py"
        self._drone   = drone

    # dest_rel_alt - meters
    def is_reached_to_relative_alt(self, dest_rel_alt, threshold=0.5):
        curr_rel_alt = self._drone.telemetry().get_global_position()["relative_alt"]

        Logger.PrintLog(self.LOG_INFO, "is_reached_to_relative_alt() - Current relative altitude: {}, Destination relative altitude: {}, Threshold: {}."
                        .format(str(curr_rel_alt), str(dest_rel_alt), str(threshold)))

        if dest_rel_alt - threshold <= curr_rel_alt <= dest_rel_alt + threshold:
            Logger.PrintLog(self.LOG_INFO, "is_reached_to_relative_alt() - Returning True.")
            return True

        Logger.PrintLog(self.LOG_INFO, "is_reached_to_relative_alt() - Returning False.")
        return False

    def is_reached_to_global_position(self, dest_lat, dest_lon, dest_rel_alt, threshold=0.5, acceptance_radius=1):
        if self.is_reached_to_relative_alt(dest_rel_alt, threshold):
            curr_global_pos = self._drone.telemetry().get_global_position()

            current_pos = {
                "lat" : curr_global_pos["lat"],
                "lon" : curr_global_pos["lon"]
            }

            dest_pos = {
                "lat" : dest_lat,
                "lon" : dest_lon
            }

            dist_to_dest = Math.calculate_global_position_distance(current_pos, dest_pos)

            Logger.PrintLog(self.LOG_INFO, "is_reached_to_global_position() - Current lat: {}, Current lon: {}, Current relative alt: {}, Destination lat: {}, Destination lon: {}, Destination relative altitude: {}, Threshold: {}."
                            .format(str(current_pos["lat"]), str(current_pos["lon"]), str(curr_global_pos["relative_alt"]), str(dest_pos["lat"]), str(dest_pos["lon"]), str(dest_rel_alt), str(threshold)))

            if (acceptance_radius == 0 and dist_to_dest <= threshold) \
            or dist_to_dest <= acceptance_radius:
                Logger.PrintLog(self.LOG_INFO, "is_reached_to_global_position() - Returning True.")
                return True
            else:
                Logger.PrintLog(self.LOG_INFO, "is_reached_to_global_position() - Distance to destination: {} m."
                                .format(str(dist_to_dest)))

        Logger.PrintLog(self.LOG_INFO, "is_reached_to_global_position() - Returning False.")
        return False

    def is_reached_to_local_position(self, dest_x, dest_y, dest_z, threshold=0.1):
        curr_local_pos = self._drone.telemetry().get_local_position()

        if dest_z - threshold <= curr_local_pos["z"] <= dest_z + threshold:
            dist_to_dest = EB_Math.TwoDimensional.distance_between_two_points(
                                (curr_local_pos["x"], curr_local_pos["y"]),
                                (dest_x, dest_y)
                            )

            Logger.PrintLog(self.LOG_INFO, "is_reached_to_local_position() - Current X: {}, Current Y: {}, Current Z: {}, Destination X: {}, Destination Y: {}, Destination Z: {}, Threshold: {}."
                            .format(str(curr_local_pos["x"]), str(curr_local_pos["y"]), str(curr_local_pos["z"]), str(dest_x), str(dest_y), str(dest_z), str(threshold)))

            if dist_to_dest <= threshold:
                Logger.PrintLog(self.LOG_INFO, "is_reached_to_local_position() - Returning True.")
                return True
            else:
                Logger.PrintLog(self.LOG_INFO, "is_reached_to_local_position() - Distance to destination: {} m."
                                .format(str(dist_to_dest)))

        Logger.PrintLog(self.LOG_INFO, "is_reached_to_local_position() - Returning False.")
        return False

    def calculate_global_heading_from_relative_heading(self, heading_angle):
        return (self._drone.telemetry().get_heading()[0] + heading_angle) % 360
