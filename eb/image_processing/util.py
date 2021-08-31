"""
    Author: Ege Bilecen
    Date  : 05.09.2020
"""
from typing import List, Tuple

from eb.math    import Math
from eb.compass import Compass

class Util:
    CAMERA_RESOLUTION   = (640, 480)
    CAMERA_CENTER_POINT = (int(CAMERA_RESOLUTION[0] / 2), int(CAMERA_RESOLUTION[1] / 2))

    class Point:
        @staticmethod
        def filter_neighbor_points(points  : List[Tuple[int, int]],
                                   distance: int) -> List[Tuple[int, int]]:
            point_list      = points.copy()
            filtered_points = []
            non_neighbors   = 0

            if len(point_list) < 2:
                return point_list

            for index_i, i in enumerate(point_list):
                to_delete_list  = [] # indexes
                delete_count    = 0
                found_neighbors = 0
                mean_center = {
                    "x" : 0,
                    "y" : 0
                }

                for index_j, j in enumerate(point_list):
                    if i == j: continue

                    dist = Math.TwoDimensional.distance_between_two_points(i, j)

                    if dist <= distance:
                        found_neighbors += 1
                        mean_center["x"] += j[0]
                        mean_center["y"] += j[1]
                        to_delete_list.append(index_j)

                if found_neighbors == 0:
                    non_neighbors += 1
                    filtered_points.append(i)
                    continue

                mean_center["x"] /= found_neighbors
                mean_center["y"] /= found_neighbors

                filtered_points.append((int(mean_center["x"]), int(mean_center["y"])))

                for index in to_delete_list:
                    point_list.pop(index - delete_count)
                    delete_count += 1

            if len(filtered_points) == non_neighbors:
                return filtered_points

            return Util.Point.filter_neighbor_points(filtered_points, distance)

        @staticmethod
        def extract_information(point: Tuple[int, int]) -> Tuple[float, int]:
            dist    = Math.TwoDimensional.distance_between_two_points(Util.CAMERA_CENTER_POINT, point)
            bearing = Compass.atan2_mapped_deg_to_compass_deg(
                              Math.TwoDimensional.angle_between_two_points(Util.CAMERA_CENTER_POINT, point))

            return dist, bearing

        @staticmethod
        def extract_information_from_list(point_list: List[Tuple[int, int]]) -> List[Tuple[int, int, float, int]]:
            ret_point_list = []

            for point in point_list:
                ret_point_list.append(point + Util.Point.extract_information(point))

            return ret_point_list

        @staticmethod
        def get_closer_point_to_center(point_list: List[Tuple[int, int]]) -> Tuple[int, int]:
            ret_point = None
            dist = 0

            for point in point_list:
                dist_to_center = Math.TwoDimensional.distance_between_two_points(Util.CAMERA_CENTER_POINT, point)

                if ret_point is None \
                or dist_to_center < dist:
                    ret_point = point
                    dist = dist_to_center

            return ret_point
