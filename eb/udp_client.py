"""
    Author: Ege Bilecen
    Date  : 22.07.2020

    /!\ This class is not tested yet!
    /!\ Max packet size: 65500 bytes
"""
from typing import Callable, Optional, Tuple
from time   import sleep
import socket
import threading

from eb.logger import Logger
import config
import eb.telemetry as telemetry

class UDP_Client:
    def __init__(self,
                 port   : Optional[int]      = None,
                 handler: Optional[Callable] = None) -> None:
        self.LOG_INFO = "udp_client.py"

        self._port     = port
        self._socket   = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self._data     = {} # see _thread_handler
        self._storage  = {
            "variable_list" : {}
        } # see _thread_handler
        self._handler  = None

        self._read_timeout  = 0
        self._write_timeout = 0

        # 0 - Not running
        # 1 - Running
        self._status = 0

        if  self._port \
        and callable(handler):
            self._status = 1

            self._socket.bind(("", self._port))

            t = threading.Thread(target=self._thread_handler, args=(self,))
            t.daemon = False
            t.start()

    # Private Method(s)
    def _reset(self):
        __var_list = self._storage["variable_list"]

        self.__init__(self._port, self._handler)

        self._storage["variable_list"] = __var_list

    @staticmethod
    def _thread_handler(cls) -> None:
        LOG_INFO = cls.LOG_INFO + "_thread_handler()"

        while cls.get_status():
            try:
                cls._socket.settimeout(cls.get_read_timeout())
                recv_data, addr = cls._socket.recvfrom(config.Connection.BUFFER_SIZE)

                addr_str = UDP_Client.get_addr_str(addr)

                if recv_data == b"":
                    Logger.PrintLog(LOG_INFO, "Connection with server has been lost.")
                    raise ConnectionAbortedError

                if addr_str not in cls._data:
                    cls._data[addr_str] = {}

                if addr_str not in cls._storage:
                    cls._storage[addr] = {
                        "last_packet_type": telemetry.Packet.Type.UNKNOWN,
                        "failure_tracker" : {}
                    }

                packet_type    = telemetry.Packet.get_type(recv_data, just_start=True)
                is_data_append = False

                if  not cls.get_is_packet_type_exist(addr_str, packet_type) \
                and packet_type != telemetry.Packet.Type.UNKNOWN:
                    cls.set_packet_data(addr_str, packet_type, b"")

                if  packet_type == telemetry.Packet.Type.MESSAGE \
                and packet_type == telemetry.Packet.Message.Response.CLEAR:
                    del cls._data
                    cls.set_last_packet_type(addr_str, telemetry.Packet.Type.MESSAGE)
                    Logger.PrintLog(LOG_INFO, "Recieved clear request from server. Clearing storage.")
                    continue

                # UNKNOWN PACKET
                if  packet_type == telemetry.Packet.Type.UNKNOWN \
                and cls.get_last_packet_type(addr_str) == telemetry.Packet.Type.UNKNOWN:
                    cls.set_last_packet_type(addr_str, telemetry.Packet.Type.UNKNOWN)
                    Logger.PrintLog(LOG_INFO, "Got unknown packet. ({})".format(str(recv_data)))
                    continue
                else:
                    # Continuation of previous packet(s)
                    if packet_type == telemetry.Packet.Type.UNKNOWN:
                        packet_type    = cls.get_last_packet_type(addr_str)
                        is_data_append = True

                    cls.set_packet_data(addr_str,
                                        packet_type,
                                        recv_data,
                                        is_data_append)
                    cls.set_last_packet_type(addr_str,
                                             packet_type)

                if callable(cls._handler):
                    cls._handler(addr, cls)
            except Exception as ex:
                cls.exception_handler(__file__, ex)

    # Public Method(s)
    @staticmethod
    def get_addr_str(addr: Tuple[str, int]) -> str:
        return addr[0]+":"+str(addr[1])

    @staticmethod
    def get_addr_from_str(addr_str: str) -> Tuple[str, int]:
        data_split = addr_str.split(":")

        return data_split[0], int(data_split[1])

    def get_status(self) -> bool:
        if self._status == 1: return True

        return False

    def stop(self) -> None:
        if self._status == 1:
            self._status = 0
            self._socket.close()

    def send(self,
             addr   : Tuple[str, int],
             data   : bytes,
             timeout: bool = False) -> None:
        self.delete_packet_data(UDP_Client.get_addr_str(addr), telemetry.Packet.Type.MESSAGE)

        if timeout: self._socket.settimeout(self.get_write_timeout())

        self._socket.sendto(data, addr)

    def set_read_timeout(self,
                        timeout: int = 5) -> None:
        if timeout < 0: timeout = 0
        self._read_timeout = timeout

    def get_read_timeout(self) -> any:
        if self._read_timeout == 0: return None

        return self._read_timeout

    def set_write_timeout(self,
                          timeout: int = 5) -> None:
        if timeout < 0: timeout = 0
        self._write_timeout = timeout

    def get_write_timeout(self) -> any:
        if self._write_timeout == 0: return None

        return self._write_timeout

    def set_packet_data(self,
                        addr_str   : str,
                        packet_type: int,
                        data       : any,
                        append_mode: bool = False) -> None:
        if not self.get_is_packet_type_exist(addr_str, packet_type): self._data[addr_str][packet_type] = None

        if append_mode:
            self._data[addr_str][packet_type] = self._data[addr_str][packet_type] + data

        self._data[addr_str][packet_type] = data

    def get_packet_data(self,
                        addr_str   : str,
                        packet_type: int,
                        extract    : bool = False) -> any:
        if not self.get_is_packet_type_exist(addr_str, packet_type): return None

        data = self._data[addr_str][packet_type]

        if extract:
            try:
                return telemetry.Packet.get_class_by_type(packet_type).extract(data)
            except AttributeError:
                Logger.PrintLog(self.LOG_INFO, "get_packet_data() - [WARNING] - Packet type ({}) doesn't have extract method."
                                .format(str(packet_type)))

        return data

    def clear_packet_data(self,
                          addr_str   : str,
                          packet_type: int) -> None:
        if not self.get_is_packet_type_exist(addr_str, packet_type): return

        self._data[addr_str][packet_type] = None

    def delete_packet_data(self,
                           addr_str   : str,
                           packet_type: int) -> None:
        if not self.get_is_packet_type_exist(addr_str, packet_type): return

        del self._data[addr_str][packet_type]

    def get_is_packet_type_exist(self,
                                 addr_str   : str,
                                 packet_type: int) -> bool:
        if addr_str in self._data:
            if packet_type in self._data[addr_str]: return True
        else: self._data[addr_str] = {}

        return False

    def set_last_packet_type(self,
                             addr_str   : str,
                             packet_type: int) -> None:
        try: self._storage[addr_str]["last_packet_type"] = packet_type
        except KeyError: return

    def get_last_packet_type(self,
                             addr_str: str) -> Optional[int]:
        try: return self._storage[addr_str]["last_packet_type"]
        except KeyError: return None

    def get_failure_tracker(self,
                            addr_str: str) -> any:
        try: return self._storage[addr_str]["failure_tracker"]
        except KeyError: return None

    def set_variable(self,
                     key : str,
                     val : any) -> None:
        self._storage["variable_list"][key] = val

    def get_variable(self,
                     key : str) -> any:
        if not key in self._storage["variable_list"]: return None

        return self._storage["variable_list"][key]

    def exception_handler(self,
                          file: str,
                          ex  : Exception) -> None:
        self._status = 0

        file = file.split("\\")[-1].split("/")[-1]
        LOG_INFO = "udp_client.py - exception_handler() - called by "+file
        ex_str  = str(ex).lower()
        ex_type = type(ex)

        if   ex_type == socket.timeout:
            Logger.PrintLog(LOG_INFO, "Connection with server has been timeouted.")
        elif ex_type == ConnectionResetError:
            Logger.PrintLog(LOG_INFO, "Connection with server has been reseted.")
        elif ex_type == ConnectionRefusedError:
            Logger.PrintLog(LOG_INFO, "Cannot connect to server. Connection refused.")
            sleep(config.Connection.CONNECT_DELAY)
        elif ex_type == ConnectionAbortedError:
            Logger.PrintLog(LOG_INFO, "Connection with server has been aborted.")
        elif ex_type == OSError \
        and  "winerror 10056" in ex_str:
            Logger.PrintLog(LOG_INFO, "Connection with server forced to be closed.")
        else:
            Logger.PrintException(LOG_INFO + " - UNKNOWN EXCEPTION", ex)

        self._socket.close()
        self._reset()
