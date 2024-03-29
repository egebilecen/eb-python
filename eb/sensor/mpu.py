from time import sleep
import threading

from eb.i2c import I2C
from eb.time import Time

class MPU:
    class REGISTER:
        PWR_MGMT_1        = 0x6B
        STATUS            = 0x3A

        ACCEL_DATA        = 0x3B
        GYRO_DATA         = 0x43

        ACCEL_SENSITIVITY = 0x1C
        GYRO_SENSITIVITY  = 0x1B

    def __init__(self,
                 addr         : int  = 0x68,
                 data_rate_hz : int  = 10,
                 enable_mag   : bool = False) -> None:
        self._addr      = addr
        self._data_rate = data_rate_hz
        self._gyro_acc  = I2C(addr)
        self._last_data = {}
        self._status    = 0

        self._enable_mag = enable_mag

    @staticmethod
    def _parse_gyro_acc_val(val : int) -> int:
        if val > 0x7FFF: return -(65535 - val)
        return val

    @staticmethod
    def _thread_handler(cls) -> None:
        while cls._status:
            try:
                ### Accelometer / Gyroscope
                block_data = cls._gyro_acc.read_block_data(MPU.REGISTER.STATUS, 1)

                if not block_data[0] & 0x01:
                    continue

                # Accel data
                block_data = cls._gyro_acc.read_block_data(MPU.REGISTER.ACCEL_DATA, 6)
                
                accel_data = {
                    "raw": {
                        "x" : MPU._parse_gyro_acc_val((block_data[0] << 8) | block_data[1]),
                        "y" : MPU._parse_gyro_acc_val((block_data[2] << 8) | block_data[3]),
                        "z" : MPU._parse_gyro_acc_val((block_data[4] << 8) | block_data[5])
                    },
                    "scaled": {}
                }

                accel_data["scaled"] = {
                    "x" : MPU._parse_gyro_acc_val(accel_data["raw"]["x"]) / 2048.,
                    "y" : MPU._parse_gyro_acc_val(accel_data["raw"]["y"]) / 2048.,
                    "z" : MPU._parse_gyro_acc_val(accel_data["raw"]["z"]) / 2048.
                }

                # Gyro data
                block_data = cls._gyro_acc.read_block_data(MPU.REGISTER.GYRO_DATA, 6)
                
                gyro_data = {
                    "raw": {
                        "x" : MPU._parse_gyro_acc_val((block_data[0] << 8) | block_data[1]),
                        "y" : MPU._parse_gyro_acc_val((block_data[2] << 8) | block_data[3]),
                        "z" : MPU._parse_gyro_acc_val((block_data[4] << 8) | block_data[5]),
                    },
                    "scaled": {}
                }

                gyro_data["scaled"] = {
                    "x" : MPU._parse_gyro_acc_val(gyro_data["raw"]["x"]) / 16.4,
                    "y" : MPU._parse_gyro_acc_val(gyro_data["raw"]["y"]) / 16.4,
                    "z" : MPU._parse_gyro_acc_val(gyro_data["raw"]["z"]) / 16.4
                }

                cls._last_data = {
                    "accel"     : accel_data,
                    "gyro"      : gyro_data,
                    "timestamp" : Time.get_current_timestamp("ms")
                }
            except TypeError: pass

            sleep(1 / cls._data_rate)

    def start(self) -> None:
        ### Accelometer / Gyroscope settings
        self._gyro_acc.write_byte(MPU.REGISTER.PWR_MGMT_1, 0x00)

        # Accel Sensitivity
        # 0, 8, 16 and 24 (int) for 16384, 8192, 4096 and 2048 sensitivity respectively
        self._gyro_acc.write_byte(MPU.REGISTER.ACCEL_SENSITIVITY, 0x18)

        # Gyro Sensitivity
        # 0, 8, 16 and 24 (int) for 131, 65.5, 32.8 and 16.4 sensitivity respectively
        self._gyro_acc.write_byte(MPU.REGISTER.GYRO_SENSITIVITY, 0x18)

        # Magnetometer
        # Enable
        if self._enable_mag:
            self._gyro_acc.write_byte(0x37, 0x02)
            self._gyro_acc.write_byte(0x6a, 0x00)
            self._gyro_acc.write_byte(0x6b, 0x00)

        self._status = 1

        t = threading.Thread(target=self._thread_handler, args=(self,))
        t.daemon = False
        t.start()

    def stop(self) -> None:
        self._status = 0

    def get_last_data(self) -> dict:
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
