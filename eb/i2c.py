from smbus2 import SMBus

from eb.logger import Logger
from eb.method import Method

class I2C:
    def __init__(self, 
                 base_addr: int,
                 bus_no   : int = 1):
        self._bus  = None
        self._addr = base_addr

        try:
            self._bus = SMBus(bus_no)
        except Exception as ex:
            Logger.PrintException("i2c.py" + " - __init__()", ex)
            return

    def read_block_data(self, register, length, addr_ovr=None):
        addr = self._addr

        if addr_ovr: addr = addr_ovr

        def impl():
            try:
                return self._bus.read_i2c_block_data(addr, register, length)
            except OSError:
                return False
            except Exception as ex:
                Logger.PrintException("i2c.py" + " - read_block_data()", ex)

        return Method.Repeat.until_value_not(impl, (), 40, 25, False)[1]

    def write_byte(self, register, byte, addr_ovr=None):
        addr = self._addr

        if addr_ovr: addr = addr_ovr

        def impl():
            try:
                self._bus.write_byte_data(addr, register, byte)
            except OSError:
                return False
            except Exception as ex:
                Logger.PrintException("i2c.py" + " - write_byte()", ex)

        return Method.Repeat.until_value_not(impl, (), 40, 25, False)[0]
