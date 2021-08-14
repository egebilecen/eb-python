"""
    Author: Ege Bilecen
    Date  : 26.07.2020

    Datasheet:
    https://stanford.edu/class/ee267/misc/MPU-9255-Datasheet.pdf

    Register Map:
    https://stanford.edu/class/ee267/misc/MPU-9255-Register-Map.pdf

    I2C Library Reference:
    https://pypi.org/project/smbus2/
"""
from typing import Optional
from smbus2 import SMBus
from time   import sleep
import threading

from eb.time   import Time
from eb.logger import Logger
from eb.method import Method

class MPU9255:
    class REGISTER:
        PWR_MGMT_1   = 0x6B
        STATUS       = 0x3A

        ACCEL_DATA   = 0x3B
        GYRO_DATA    = 0x43

        ACCEL_CONFIG = 0x1C
        GYRO_CONFIG  = 0x1B

    def __init__(self,
                 base_addr: int = 0x68,
                 data_rate: int = 10) -> None:
        self.LOG_INFO = "mpu9255.py"

        self._bus       = None
        self._addr      = base_addr
        self._data_rate = data_rate
        self._last_data = {}
        self._status    = 0

        try:
            self._bus = SMBus(1)
        except Exception as ex:
            Logger.PrintException(self.LOG_INFO + " - __init__()", ex)
            return

    # Private Method(s)
    def _read_block_data(self, register, length, addr_ovr=None):
        addr = self._addr

        if addr_ovr: addr = addr_ovr

        def impl():
            try:
                return self._bus.read_i2c_block_data(addr, register, length)
            except OSError:
                return False

        return Method.Repeat.until_value_not(impl, (), 40, 25, False)[1]

    def _write_byte(self, register, byte, addr_ovr=None):
        addr = self._addr

        if addr_ovr: addr = addr_ovr

        def impl():
            try:
                self._bus.write_byte_data(addr, register, byte)
            except OSError:
                return False

        return Method.Repeat.until_value_not(impl, (), 40, 25, False)[0]

    @staticmethod
    def _parse_val(val):
        if val > 0x7FFF: return -(65535 - val)
        return val

    @staticmethod
    def _thread_handler(cls) -> None:
        while cls._status:
            try:
                block_data = cls._read_block_data(MPU9255.REGISTER.STATUS, 1)

                if not block_data[0] & 0x01:
                    continue

                # Accel data
                block_data = cls._read_block_data(MPU9255.REGISTER.ACCEL_DATA, 6)
                accel_data = {
                    "raw": {
                        "x": MPU9255._parse_val((block_data[0] << 8) | block_data[1]),
                        "y": MPU9255._parse_val((block_data[2] << 8) | block_data[3]),
                        "z": MPU9255._parse_val((block_data[4] << 8) | block_data[5])
                    },
                    "scaled": {}
                }
                accel_data["scaled"] = {
                    "x": MPU9255._parse_val(accel_data["raw"]["x"]) / 2048.,
                    "y": MPU9255._parse_val(accel_data["raw"]["y"]) / 2048.,
                    "z": MPU9255._parse_val(accel_data["raw"]["z"]) / 2048.
                }

                # Gyro data
                block_data = cls._read_block_data(MPU9255.REGISTER.GYRO_DATA, 6)
                gyro_data = {
                    "raw": {
                        "x": MPU9255._parse_val((block_data[0] << 8) | block_data[1]),
                        "y": MPU9255._parse_val((block_data[2] << 8) | block_data[3]),
                        "z": MPU9255._parse_val((block_data[4] << 8) | block_data[5]),
                    },
                    "scaled": {}
                }
                gyro_data["scaled"] = {
                    "x": MPU9255._parse_val(gyro_data["raw"]["x"]) / 16.4,
                    "y": MPU9255._parse_val(gyro_data["raw"]["y"]) / 16.4,
                    "z": MPU9255._parse_val(gyro_data["raw"]["z"]) / 16.4
                }

                cls._last_data = {
                    "accel": accel_data,
                    "gyro" : gyro_data,
                    "timestamp": Time.get_current_timestamp("ms")
                }
            except TypeError: pass

            sleep(1 / cls._data_rate)

    # Public Method(s)
    def start(self) -> None:
        if self._bus is None:
            Logger.PrintLog(self.LOG_INFO, "start() - Cannot start. self._bus is None.")
            return

        self._write_byte(MPU9255.REGISTER.PWR_MGMT_1, 0x00)

        # Accel
        # 0, 8, 16 and 24 (int) for 16384, 8192, 4096 and 2048 sensitivity respectively
        self._write_byte(MPU9255.REGISTER.ACCEL_CONFIG, 0x18) # set to 2048

        # Gyro
        # 0, 8, 16 and 24 (int) for 131, 65.5, 32.8 and 16.4 sensitivity respectively
        self._write_byte(MPU9255.REGISTER.GYRO_CONFIG, 0x18) # set to 16.4

        self._status = 1

        t = threading.Thread(target=self._thread_handler, args=(self,))
        t.daemon = False
        t.start()

    def stop(self) -> None:
        self._status = 0

    def get_is_started(self) -> bool:
        if self._status == 1: return True

        return False

    def get_last_data(self) -> Optional[dict]:
        if self._last_data == {}:
            return {
                "accel" : {
                    "raw" : {
                        "x" : None,
                        "y" : None,
                        "z" : None
                    },
                    "scaled" : {
                        "x" : None,
                        "y" : None,
                        "z" : None
                    }
                },
                "gyro"  : {
                    "raw" : {
                        "x" : None,
                        "y" : None,
                        "z" : None
                    },
                    "scaled" : {
                        "x" : None,
                        "y" : None,
                        "z" : None
                    }
                },
                "timestamp" : Time.get_current_timestamp("ms")
            }

        return self._last_data
