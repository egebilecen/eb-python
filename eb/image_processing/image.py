"""
    Author: Ege Bilecen
    Date  : 04.08.2020
"""
import cv2

class Image:
    class Encode:
        @staticmethod
        def FromRawImage(frame     : bytes,
                         extension : str = ".jpg") -> bytes:
            _, encoded_frame = cv2.imencode(extension, frame)
            return encoded_frame.tobytes()
