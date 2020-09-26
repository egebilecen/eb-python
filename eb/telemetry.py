"""
    Author: Ege Bilecen
    Date  : 21.07.2020
"""
import hashlib
import struct

from eb.time    import Time
from eb.convert import Convert
import config

class Packet:
    LITTLE_ENDIAN = 1
    BIG_ENDIAN    = 2
    BYTE_ORDER    = 1 # LITTLE_ENDIAN is default

    class Type:
        UNKNOWN             = 0
        MESSAGE             = 1
        STRING_MESSAGE      = 2
        DATA_TRANSMISSION   = 3
        CAMERA_TRANSMISSION = 4
        TELEMETRY           = 5

        class Special:
            TRANS_DATA = -1

    @staticmethod
    def set_byte_order(order: int) -> None:
        if order != Packet.LITTLE_ENDIAN \
        or order != Packet.BIG_ENDIAN: return

        Packet.BYTE_ORDER = order

    @staticmethod
    def get_md5(byte_array : bytes) -> bytes:
        return hashlib.md5(byte_array).digest()

    @staticmethod
    def convert_to_int(byte_data: bytes,
                       signed   : bool = False) -> int:
        if Packet.BYTE_ORDER == Packet.BIG_ENDIAN:
            byte_order = "big"
        else:
            byte_order = "little"

        return int.from_bytes(byte_data, signed=signed, byteorder=byte_order)

    @staticmethod
    def get_type(byte_array: bytes,
                 just_start: bool = False) -> int:
        if  byte_array[:2] == Packet.Message.start_bytes:
            if just_start \
            or byte_array[-2:] == Packet.Message.end_bytes:
                return Packet.Type.MESSAGE

        if  byte_array[:2] == Packet.StringMessage.start_bytes:
            if just_start \
            or byte_array[-2:] == Packet.StringMessage.end_bytes:
                return Packet.Type.STRING_MESSAGE

        if  byte_array[:2] == Packet.Data.start_bytes:
            if just_start \
            or byte_array[-2:] == Packet.Data.end_bytes:
                return Packet.Type.DATA_TRANSMISSION

        if  byte_array[:2] == Packet.Camera.start_bytes:
            if just_start \
            or byte_array[-2:] == Packet.Camera.end_bytes:
                return Packet.Type.CAMERA_TRANSMISSION

        if  byte_array[:2] == Packet.Telemetry.start_bytes:
            if just_start \
            or byte_array[-2:] == Packet.Telemetry.end_bytes:
                return Packet.Type.TELEMETRY

        return Packet.Type.UNKNOWN

    @staticmethod
    def get_class_by_type(packet_type) -> any:
        if   packet_type == Packet.Type.MESSAGE:
            return Packet.Message
        elif packet_type == Packet.Type.STRING_MESSAGE:
            return Packet.StringMessage
        elif packet_type == Packet.Type.DATA_TRANSMISSION:
            return Packet.Data
        elif packet_type == Packet.Type.CAMERA_TRANSMISSION:
            return Packet.Camera
        elif packet_type == Packet.Type.TELEMETRY:
            return Packet.Telemetry

        return None

    class Message:
        class Response:
            UNKNOWN     = b"\x00\x00\x00\x00"
            ACKNOWLEDGE = b"\xEC\x17\x09\x77"
            CLEAR       = b"\xCC\x77\xEE\x44"

        start_bytes = b"\x03\x63"
        end_bytes   = b"\xB1\x73"

        @classmethod
        def prepare(cls, byte_data: bytes) -> bytes:
            packet = b""

            packet += cls.start_bytes
            packet += byte_data
            packet += cls.end_bytes

            return packet

        @staticmethod
        def extract(byte_data: bytes) -> dict:
            data = byte_data[2:-2]

            return {
                "data" : data
            }

    class StringMessage:
        start_bytes = b"\xE7\xD4"
        end_bytes   = b"\x31\x62"

        @classmethod
        def prepare(cls, text: str) -> bytes:
            packet = b""

            packet += cls.start_bytes
            packet += text.encode("ascii")
            packet += cls.end_bytes

            return packet

        @staticmethod
        def extract(byte_data: bytes) -> dict:
            data = byte_data[2:-2]

            return {
                "data" : data.decode("ascii")
            }

    class Data:
        class Response:
            FAILURE = b"\xDE\x00\x00\xAD"
            SUCCESS = b"\xDE\x01\x01\xAD"

        start_bytes   = b"\xCA\xFE"
        end_bytes     = b"\xBE\xEF"
        
        @staticmethod
        def extract(byte_data: bytes) -> dict:
            chunk_count   = byte_data[2]
            packet_number = byte_data[3]
            data_size     = Packet.convert_to_int(byte_data[4:8])
            data_str      = Convert.bytes_to_ascii(byte_data[8:24])
            file_mode     = byte_data[24:25]
            recv_md5      = byte_data[25:41]
            data          = byte_data[41:41+data_size]

            return {
                "chunk_count"   : chunk_count,
                "packet_number" : packet_number,
                "data_size"     : data_size,
                "data_str"      : data_str,
                "file_mode"     : file_mode,
                "recv_md5"      : recv_md5,
                "data"          : data
            }

        @classmethod
        def check_is_valid(cls,
                           byte_data: bytes) -> bool:
            if  byte_data[:2]  == cls.start_bytes  \
            and byte_data[-2:] == cls.end_bytes:
                packet_data = cls.extract(byte_data)
                
                if  packet_data["data_size"] == len(packet_data["data"]) \
                and Packet.get_md5(packet_data["data"]) == packet_data["recv_md5"]:
                    return True
                else: 
                    return False
                
            return False

    class Camera:
        start_bytes = b"\x5E\x81"
        end_bytes   = b"\x17\xBA"

        @classmethod
        def prepare(cls,
                    data: bytes) -> bytes:
            packet = b""

            packet += cls.start_bytes
            packet += data
            packet += cls.end_bytes

            return packet

    class Telemetry:
        start_bytes = b"\xBA\xAD"
        end_bytes   = b"\xF0\x0D"

        @classmethod
        def prepare(cls, var) -> bytes:
            """
            [Example usage]
                packet = b""

                packet += cls.start_bytes

                # Team Number
                packet += struct.pack("<H", config.Satellite.TEAM_NUMBER)

                # Packet Number
                packet += struct.pack("<H", packet_no)

                # Sent Date
                packet += struct.pack("<I", Time.get_current_timestamp())

                # Pressure
                packet += struct.pack("<f", pressure)

                return packet
            """
            raise NotImplementedError
