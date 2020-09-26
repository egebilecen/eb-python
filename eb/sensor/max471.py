"""
    Author: Ege Bilecen
    Date  : 26.07.2020
"""
from typing import Optional
import threading

from eb.sensor.ads1115 import ADS1115
from eb.time           import Time
from eb.logger         import Logger

class MAX471:
    def __init__(self,
                 ads1115  : ADS1115,
                 channel  : int = 0) -> None:
        self.LOG_INFO   = "max471.py"

        self._adc       = ads1115
        self._channel   = channel
        self._last_data = {}
        self._status    = 0

    # Private Method(s)
    @staticmethod
    def _thread_handler(cls) -> None:
        while cls._status:
            voltage = cls._adc.get_last_data()
            if voltage is None: continue

            voltage = voltage[cls._channel]["voltage"] / (10 ** 3) # V
            voltage = voltage * 5. / 1023. # max471 conversion

            cls._last_data = {
                "voltage"   : voltage,
                "timestamp" : Time.get_current_timestamp("ms")
            }

    # Public Method(s)
    def start(self) -> None:
        if not self._adc.get_is_started():
            Logger.PrintLog(self.LOG_INFO, "start() - Cannot start. self._adc is not started.")
            return

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
                "voltage"  : None,
                "timestamp": Time.get_current_timestamp("ms")
            }

        return self._last_data
