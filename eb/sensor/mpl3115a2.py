"""
    Author: Ege Bilecen
    Date  : 26.07.2020

    Datasheet:
    https://pdf.direnc.net/upload/mpl3115a2-sensor-datasheet.pdf
"""
from typing import Optional
from smbus2 import SMBus
from time   import sleep
import threading

from eb.time   import Time
from eb.logger import Logger
from eb.method import Method

class MPL3115A2:
        class REGISTER:
            PRESSURE_DATA    = 0x01
            TEMPERATURE_DATA = 0x04
            DATA_CONFIG      = 0x13
            CONTROL_1        = 0x26

        def __init__(self,
                     base_addr         : int = 0x68,
                     data_rate         : int = 10) -> None:
            self.LOG_INFO = "mpl3115a2.py"

            self._addr      = base_addr
            self._bus       = None
            self._sensor    = None
            self._data_rate = data_rate
            self._last_data = {
                "pressure"   : None,  # pascal (kPa)
                "altitude"   : None,  # meters
                "temperature": None,  # degree C,
                "timestamp"  : Time.get_current_timestamp("ms")
            }
            self._status    = 0
            self._next_measurement_type = 0 # 1- Altimeter, 2- Barometer

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
        def _thread_handler(cls) -> None:
            while cls._status:
                try:
                    block_data = cls._read_block_data(0x00, 6)

                    if block_data[0] & 0x08:
                        pressure_raw = ((block_data[1] << 16
                                         | block_data[2] << 8
                                         | block_data[3]) >> 4) / 16.0

                        temp_raw = ((block_data[4] << 8
                                     | block_data[5]) >> 4) / 16.0

                        cls._last_data["temperature"] = temp_raw

                        if cls._next_measurement_type == 1:
                            cls._last_data["altitude"] = pressure_raw
                            cls._next_measurement_type = 2

                            cls._write_byte(MPL3115A2.REGISTER.CONTROL_1, 0x39)
                        elif cls._next_measurement_type == 2:
                            cls._last_data["pressure"] = pressure_raw * 16 / 4.0 / 1000.0
                            cls._next_measurement_type = 1

                            cls._write_byte(MPL3115A2.REGISTER.CONTROL_1, 0xB9)
                            sleep(1)

                        cls._last_data["timestamp"] = Time.get_current_timestamp("ms")
                except TypeError: pass

                sleep(1 / cls._data_rate)

        # Public Method(s)
        def start(self) -> None:
            if self._bus is None:
                Logger.PrintLog(self.LOG_INFO, "start() - Cannot start. self._bus is None.")
                return

            self._write_byte(MPL3115A2.REGISTER.CONTROL_1,   0xB9)
            self._write_byte(MPL3115A2.REGISTER.DATA_CONFIG, 0x07)

            self._next_measurement_type = 1
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
                    "pressure"   : None,
                    "altitude"   : None,
                    "temperature": None,
                    "timestamp"  : Time.get_current_timestamp("ms")
                }

            return self._last_data
