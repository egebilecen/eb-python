"""
    Author: Ege Bilecen
    Date  : 04.08.2020
"""
from eb.image_processing.color import Color

class ColorList:
    class HSV:
        RED    = [Color.HSV((   0, 110, 20 ), (  10, 255, 255 )),
                  Color.HSV(( 145, 110, 20 ), ( 180, 255, 255 ))]

        YELLOW = [Color.HSV((  15,  50, 20 ), (  40, 255, 255 ))]
