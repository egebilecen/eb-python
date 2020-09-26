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

    @staticmethod
    def bytes_to_ascii(byte_data: bytes) -> str:
        return byte_data[:byte_data.index(b"\x00")].decode("ascii")

    @staticmethod
    def byte_to_file_mode(byte: bytes) -> any:
        # 1 -> Write  mode (binary)
        # 2 -> Append mode (binary)
        # 3 -> Write  mode
        # 4 -> Append mode
        if   byte == b"\x01": return "wb"
        elif byte == b"\x02": return "ab"
        elif byte == b"\x03": return "w"
        elif byte == b"\x04": return "a"

        return None

    @staticmethod
    def none_to_int(val: any,
                    ret: int = 0):
        if val is None: return ret

        return val

    @staticmethod
    def megabytes_to_bytes(mb: int) -> int:
        return mb * 1024 * 1024

    @staticmethod
    def bytes_to_megabytes(bytes_: int) -> float:
        return bytes_ / 1024 / 1024
