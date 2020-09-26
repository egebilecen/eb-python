"""
    Author : Ege Bilecen
    Date   : 05.11.2019
    Updated: 10.09.2020 - Improved circle detection based on color.
"""
from typing import List
import cv2
import numpy as np

from eb.math import Math
from eb.image_processing.color import Color as EB_Color
from eb.image_processing.util  import Util

class Color:
    @staticmethod
    def detect_blob(frame     : np.array,
                    color_list: List[EB_Color.HSV],
                    min_area  : int = 250) -> list:
        if frame is None      : return []
        if len(color_list) < 1: return []

        cv2.GaussianBlur(frame, (11, 11), 0)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, color_list[0].get_low_values(), color_list[0].get_high_values())

        if len(color_list) > 1:
            for color in color_list[1:]:
                color_mask = cv2.inRange(hsv, color.get_low_values(), color.get_high_values())
                mask = cv2.bitwise_or(mask, color_mask)

        kernel = np.ones((5, 5), np.uint8)
        eroded = cv2.erode(mask, kernel, iterations=1)
        dilated = cv2.dilate(eroded, kernel, iterations=1)

        contours, hierarchy = cv2.findContours(dilated, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

        center_list = []

        for i, contour in enumerate(contours):
            contour_area = cv2.contourArea(contour)

            if contour_area >= min_area:
                center = cv2.boundingRect(contour)
                # sqrArea = sqrt(contourArea)

                cx = int(center[0] + center[2] / 2)
                cy = int(center[1] + center[3] / 2)

                center_list.append((cx, cy))

        return center_list

class Shape:
    @staticmethod
    def detect_corner(frame       : np.array,
                      corner_count: int,
                      min_area    : int = 250) -> list:
        if frame is None   : return []
        if corner_count < 3: return []

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        ret, thresh = cv2.threshold(gray, 127, 255, 1)

        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

        center_list = []

        for i, contour in enumerate(contours):
            contour_area = cv2.contourArea(contour)

            if contour_area >= min_area:
                approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)

                if len(approx) == corner_count:
                    center = cv2.boundingRect(contour)

                    cx = int(center[0] + center[2] / 2)
                    cy = int(center[1] + center[3] / 2)

                    center_list.append((cx, cy))

        return center_list

    @staticmethod
    def detect_circle(frame       : np.array,
                      color_list  : List[EB_Color.HSV],
                      min_area    : int = 50,
                      min_radius  : int = 50,
                      fusion_dist : int = 100,
                      filter_range: int = 100,
                      param1      : any = 100,
                      param2      : any = 30) -> list:
        if len(color_list) < 1: return []
        if frame is None      : return []

        original_frame = frame.copy()
        contour_center_list    = []
        circle_center_list     = []
        fused_data_center_list = []

        cv2.GaussianBlur(frame, (11, 11), 0)

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, color_list[0].get_low_values(), color_list[0].get_high_values())

        if len(color_list) > 1:
            for color in color_list[1:]:
                color_mask = cv2.inRange(hsv, color.get_low_values(), color.get_high_values())
                mask = cv2.bitwise_or(mask, color_mask)

        kernel  = np.ones((5, 5), np.uint8)
        eroded  = cv2.erode(mask, kernel, iterations=1)
        dilated = cv2.dilate(eroded, kernel, iterations=1)
        edited_frame = dilated

        contours, _ = cv2.findContours(edited_frame, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)[-2:]

        for cnt in contours:
            if cv2.contourArea(cnt) < min_area: continue

            x, y, w, h = cv2.boundingRect(cnt)
            center     = (x + int(w / 2), y + int(h / 2))

            contour_center_list.append(center)

        if len(contour_center_list) < 1: return []

        contour_center_list = Util.Point.filter_neighbor_points(contour_center_list, 150)

        mean_contour_list_center = (Math.TwoDimensional.mean_value_of_point_list(contour_center_list))

        crop_width  = 300
        crop_height = 300
        crop_x = int(mean_contour_list_center[0]) - int(crop_width  / 2)
        crop_y = int(mean_contour_list_center[1]) - int(crop_height / 2)

        if crop_x < 0: crop_x = 0
        if crop_y < 0: crop_y = 0

        if crop_x + crop_width > frame.shape[1]:
            crop_width -= crop_x + crop_width - frame.shape[1]

        if crop_y + crop_height > frame.shape[0]:
            crop_height -= crop_y + crop_height - frame.shape[0]

        area_of_interest = original_frame[crop_y:crop_y+crop_height, crop_x:crop_x+crop_width]

        gray_frame = cv2.cvtColor(area_of_interest, cv2.COLOR_BGR2GRAY)
        detected_circles = cv2.HoughCircles(gray_frame, cv2.HOUGH_GRADIENT, 1,
                                            minDist=30,
                                            param1=param1, param2=param2,
                                            minRadius=min_radius)

        if detected_circles is not None:
            detected_circles = np.round(detected_circles[0, :]).astype("int")

            for circle in detected_circles:
                cv2.circle(area_of_interest, (circle[0], circle[1]), 2, (0, 0, 255), 2)
                circle_center_list.append((crop_x + circle[0],
                                           crop_y + circle[1]))

        for contour_point in contour_center_list:
            to_delete_list = [] # indexes
            delete_count   = 0

            for circle_index, circle_point in enumerate(circle_center_list):
                dist = Math.TwoDimensional.distance_between_two_points(contour_point, circle_point)

                if dist <= fusion_dist:
                    fused_data_center_list.append(circle_point)

                to_delete_list.append(circle_index)

            for index in to_delete_list:
                circle_center_list.pop(index - delete_count)
                delete_count += 1

        return Util.Point.filter_neighbor_points(fused_data_center_list, filter_range)
