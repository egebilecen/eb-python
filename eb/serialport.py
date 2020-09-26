"""
Author: Ege Bilecen
Date  : 15.07.2020
"""
from typing import Optional
import serial

class SerialPort:
    def __init__(self,
                 port_name     : str,
                 baudrate      : int           = 9600,
                 timeout       : Optional[int] = 0,
                 parity        : str           = serial.PARITY_NONE,
                 stopbits      : int           = serial.STOPBITS_ONE,
                 write_timeout : Optional[int] = None) -> None:
        self.serial_port = serial.Serial(port     = port_name,
                                         baudrate = baudrate,
                                         timeout  = timeout,
                                         parity   = parity,
                                         stopbits = stopbits,
                                         write_timeout = write_timeout)
        self.serial_port.close()

    def start(self) -> None:
        self.serial_port.open()

    def stop(self) -> None:
        try: self.serial_port.close()
        except: pass

    def flush(self) -> None:
        self.serial_port.flush()

    def flush_input_buffer(self):
        self.serial_port.reset_input_buffer()

    def flush_output_buffer(self):
        self.serial_port.reset_output_buffer()

    def read(self,
             size: int = 1) -> Optional[bytes]:
        return self.serial_port.read(size)

    def read_until(self,
                   delimiter: bytes = b";") -> bytes:
        ret_data = b""

        while 1:
            data = self.read()
            ret_data += data

            if delimiter in ret_data:
                return ret_data.split(delimiter)[0]

    def write(self,
              data : bytes) -> None:
        self.serial_port.write(data)

    def in_waiting(self):
        return self.serial_port.in_waiting
