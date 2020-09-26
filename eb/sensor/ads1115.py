"""
    Author: Ege Bilecen
    Date  : 27.07.2020

    ADC Converter Datasheet:
    https://cdn-shop.adafruit.com/datasheets/ads1115.pdf

    Library:
    https://github.com/adafruit/Adafruit_Python_ADS1x15
"""
from typing import Optional, List
from time   import sleep
import Adafruit_ADS1x15
import threading

from eb.time   import Time
from eb.logger import Logger

class ADS1115:
        # Choose a gain of 1 for reading voltages from 0 to 4.09V.
        # Or pick a different gain to change the range of voltages that are read:
        #  - 2/3 = +/-6.144V
        #  -   1 = +/-4.096V
        #  -   2 = +/-2.048V
        #  -   4 = +/-1.024V
        #  -   8 = +/-0.512V
        #  -  16 = +/-0.256V
        # See table 3 in the ADS1015/ADS1115 datasheet for more info on gain.
        def __init__(self,
                     base_addr: int                 = 0x48,
                     channels : Optional[List[int]] = None,
                     gain     : int                 = 1,
                     data_rate: int                 = 10) -> None:
            self.LOG_INFO = "ads1115.py"

            if channels is None: channels = []

            self._adc       = None
            self._addr      = base_addr
            self._channels  = channels
            self._gain      = gain
            self._data_rate = data_rate
            self._last_data = {}
            self._status    = 0

            try:
                self._adc = Adafruit_ADS1x15.ADS1115(self._addr)
            except Exception as ex:
                Logger.PrintException(self.LOG_INFO + " - __init__()", ex)
                return

        # Private Method(s)
        @staticmethod
        def _thread_handler(cls) -> None:
            while cls._status:
                for channel in cls._channels:
                    if channel > 3: continue

                    try:
                        mV = cls._adc.read_adc(channel, cls._gain)
                    except OSError: continue

                    if "channel" not in cls._last_data: cls._last_data["channel"] = {}

                    cls._last_data[channel] = {
                        "voltage"   : mV,
                        "timestamp" : Time.get_current_timestamp("ms")
                    }

                sleep(1 / cls._data_rate)

        # Public Method(s)
        def start(self) -> None:
            if self._adc is None:
                Logger.PrintLog(self.LOG_INFO, "start() - Cannot start. self._adc is None.")
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
            if self._last_data == {}: return None
            return self._last_data
