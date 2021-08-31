"""
    Author: Ege Bilecen
    Date  : 21.07.2020
"""
from math import pi

class Convert:
    class Math:
        @staticmethod
        def radians_to_degrees(rad: float) -> float:
            return rad * 180 / pi

    class Value:
        @staticmethod
        def none_to_int(val: any,
                        ret: int = 0):
            if val is None: return ret

            return val

    class Byte:
        @staticmethod
        def bytes_to_ascii(byte_data: bytes) -> str:
            return byte_data[:byte_data.index(b"\x00")].decode("ascii")

        @staticmethod
        def megabytes_to_bytes(mb: int) -> int:
            return mb * 1024 * 1024

        @staticmethod
        def bytes_to_megabytes(bytes_: int) -> float:
            return bytes_ / 1024 / 1024
