"""
    Author: Ege Bilecen
    Date  : 04.08.2020
"""
class Color:
    class HSV:
        def __init__(self,
                     low_hsv : tuple,
                     high_hsv: tuple):
            self._low  = low_hsv
            self._high = high_hsv

        def get_low_values(self):
            return self._low

        def get_high_values(self):
            return self._high
