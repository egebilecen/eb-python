"""
    Author: Ege Bilecen
    Date  : 26.07.2020

    Description:
    Class for GY-NEO6MV2 GPS module.

    Default settings of module:
    * 9600 Baud
    * 8 bits
    * no parity bit
    * 1 stop bit

    Datasheet:
    https://www.rlocman.ru/i/File/2011/04/22/1.pdf

    NMEA sentences:
    https://www.gpsinformation.org/dale/nmea.htm#nmea

    GPS fix:
    0 = invalid
    1 = GPS fix (SPS)
    2 = DGPS fix
    3 = PPS fix
    4 = Real Time Kinematic
    5 = Float RTK
    6 = estimated (dead reckoning) (2.3 feature)
    7 = Manual input mode
    8 = Simulation mode
"""
from typing import Optional
import threading

from eb.logger      import Logger
from eb.serialport  import SerialPort
from eb.time        import Time

class GY_NEO6MV2:
    LINE_END = b"\r\n"

    def __init__(self,
                 port_name : str,
                 baudrate  : int = 9600) -> None:
        self.LOG_INFO = "gy_neo6mv2.py"

        self._last_data = {}
        self._serial    = None
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
            LOG_INFO = "gy_neo6mv2.py - _thread_handler()"

            try:
                gps_data = cls._serial.read_until(GY_NEO6MV2.LINE_END).decode("ascii")
                data_split = gps_data.split(",")

                if  "$GPGGA" != data_split[0] \
                and "$GNGGA" != data_split[0]: continue

                cls._last_data = {
                    "timestamp" : Time.get_current_timestamp("ms"),
                    "latitude"  : float(data_split[2]) / 100, # Degree, north
                    "longitude" : float(data_split[4]) / 100, # Degree, east
                    "fix"       : int(data_split[6]),         # Fix quality
                    "sat_count" : int(data_split[7]),         # Number of satellites being tracked
                    "altitude"  : float(data_split[9])        # Meters, above mean sea level
                }
            except ValueError:
                Logger.PrintLog(LOG_INFO, "Couldn't parse gps data. Perhaps module is still initializing?")
            except Exception as ex:
                Logger.PrintException(LOG_INFO, ex)
                continue

    # Public Method(s)
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
                "timestamp" : Time.get_current_timestamp("ms"),
                "latitude"  : None,
                "longitude" : None,
                "fix"       : None,
                "sat_count" : None,
                "altitude"  : None
            }
        return self._last_data
