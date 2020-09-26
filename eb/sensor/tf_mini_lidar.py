"""
    Author: Ege Bilecen
    Date  : 06.09.2020

    Datasheet:
    https://pdf.direnc.net/upload/tfmini-lidar-tof-lazer-mesafe-sensoru-datasheet.pdf
"""
from typing import Optional
import threading

from eb.time       import Time
from eb.logger     import Logger
from eb.serialport import SerialPort

class TF_MINI_LIDAR:
    def __init__(self,
                 port_name: str = "/dev/ttyUSB0",
                 baudrate : int = 115200) -> None:
        self.LOG_INFO = "tf_mini_lidar.py"

        self._last_data = {}
        self._port_name = port_name
        self._baudrate  = baudrate
        self._status    = 0

        try:
            self._serial = SerialPort(self._port_name, self._baudrate)
        except Exception as ex:
            Logger.PrintException(self.LOG_INFO + " - __init__()", ex)
            return

    # Private Method(s)
    @staticmethod
    def _thread_handler(cls) -> None:
        while cls._status:
            if cls._serial.in_waiting() >= 9:
                recv_data = cls._serial.read(9)

                if recv_data[:2] == b"\x59\x59":
                    distance        = (recv_data[3] << 8) | recv_data[2]
                    signal_strength = (recv_data[5] << 8) | recv_data[4]
                    mode            = recv_data[6]
                    checksum        = recv_data[8]

                    cls._last_data = {
                        "timestamp"       : Time.get_current_timestamp("ms"),
                        "distance"        : distance,
                        "signal_strength" : signal_strength,
                        "mode"            : mode
                    }

                cls._serial.flush_input_buffer()

        cls._serial.stop()

    def start(self) -> None:
        if self._serial is None:
            Logger.PrintLog(self.LOG_INFO, "start() - Cannot start. self._serial is None.")
            return

        self._serial.start()
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
                "timestamp"       : Time.get_current_timestamp("ms"),
                "distance"        : None,
                "signal_strength" : None,
                "mode"            : None
            }

        return self._last_data
