"""
    Author: Ege Bilecen
    Date  : 29.08.2020
"""
from math import sqrt, atan2, degrees

class Math:
    class Value:
        @staticmethod
        def map(val, in_min, in_max, out_min, out_max):
            if   val < in_min: return out_min
            elif val > in_max: return out_max

            return (val - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    class TwoDimensional:
        @staticmethod
        def distance_between_two_points(pt1, pt2):
            return sqrt((pt1[0] - pt2[0]) * (pt1[0] - pt2[0]) + (pt1[1] - pt2[1]) * (pt1[1] - pt2[1]))

        @staticmethod
        def angle_between_two_points(pt1, pt2, map_to_360=True):
            deg = degrees(atan2(pt2[1] - pt1[1], pt2[0] - pt1[0]))

            if map_to_360:
                return Math.Value.map(deg, -180, 180, 0, 360)

            return deg

        @staticmethod
        def mean_value_of_point_list(point_list):
            mean_val = [0, 0]

            for point in point_list:
                mean_val[0] += point[0]
                mean_val[1] += point[1]

            mean_val[0] /= len(point_list)
            mean_val[1] /= len(point_list)

            return mean_val[0], mean_val[1]
