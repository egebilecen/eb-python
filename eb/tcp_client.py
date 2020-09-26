"""
    Author: Ege Bilecen
    Date  : 22.07.2020
"""
from typing import Callable
from time   import sleep
import socket
import threading
import os

from eb.logger  import Logger
from eb.convert import Convert
import config
import eb.telemetry as telemetry

class TCP_Client:
    class Type:
        UNSPECIFIED   = 0
        RECV_ONLY     = 1
        SEND_ONLY     = 2
        SEND_AND_RECV = 3

    def __init__(self,
                 ip  : str,
                 port: int) -> None:
        self.LOG_INFO = "tcp_client.py"

        self._ip       = ip
        self._port     = port
        self._socket   = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._type     = TCP_Client.Type.UNSPECIFIED

        self._data     = {}
        self._storage  = {
            "last_packet_type": telemetry.Packet.Type.UNKNOWN,
            "failure_tracker" : {},
            "variable_list"   : {}
        }
        self._handler  = None
        self._name     = None

        self._read_timeout  = 0
        self._write_timeout = 0

        # 0 - Not running
        # 1 - Running
        self._status = 0

    # Private Method(s)
    def _reset(self):
        __handler  = self._handler
        __type     = self._type
        __var_list = self._storage["variable_list"]

        self.__init__(self._ip, self._port)

        self.set_handler(__handler)
        self.set_type(__type)
        self._storage["variable_list"] = __var_list

    @staticmethod
    def _thread_handler(cls) -> None:
        LOG_INFO = cls.LOG_INFO + "_thread_handler()"

        while cls.get_status():
            try:
                cls._socket.settimeout(cls.get_read_timeout())
                recv_data = cls._socket.recv(config.Connection.BUFFER_SIZE)

                if recv_data == b"":
                    Logger.PrintLog(LOG_INFO, "Connection with server has been lost.")
                    raise ConnectionAbortedError

                packet_type    = telemetry.Packet.get_type(recv_data, just_start=True)
                is_data_append = False

                if  not cls.get_is_packet_type_exist(packet_type) \
                and packet_type != telemetry.Packet.Type.UNKNOWN:
                    cls.set_packet_data(packet_type, b"")

                if  packet_type == telemetry.Packet.Type.MESSAGE \
                and packet_type == telemetry.Packet.Message.Response.CLEAR:
                    del cls._data
                    cls.set_last_packet_type(telemetry.Packet.Type.MESSAGE)
                    Logger.PrintLog(LOG_INFO, "Recieved clear request from server. Clearing storage.")
                    continue

                # UNKNOWN PACKET
                if  packet_type == telemetry.Packet.Type.UNKNOWN \
                and cls.get_last_packet_type() == telemetry.Packet.Type.UNKNOWN:
                    cls.set_last_packet_type(telemetry.Packet.Type.UNKNOWN)
                    Logger.PrintLog(LOG_INFO, "Got unknown packet. ({})".format(str(recv_data)))
                    continue
                else:
                    # Continuation of previous packet(s)
                    if packet_type == telemetry.Packet.Type.UNKNOWN:
                        packet_type    = cls.get_last_packet_type()
                        is_data_append = True

                    cls.set_packet_data(packet_type,
                                        recv_data,
                                        is_data_append)
                    cls.set_last_packet_type(packet_type)

                    # TODO - Add support for multiple chunks.
                    if  packet_type == telemetry.Packet.Type.DATA_TRANSMISSION:
                        packet_data = cls.get_packet_data(packet_type)

                        if telemetry.Packet.Data.check_is_valid(packet_data):
                            Logger.PrintLog(LOG_INFO, "Recieved valid data transmission packet.")

                            trans_data = telemetry.Packet.Data.extract(packet_data)
                            data_str   = trans_data["data_str"]
                            file_path  = config.BASE_DIR + data_str
                            file_mode  = Convert.byte_to_file_mode(trans_data["file_mode"])

                            if file_mode is not None:
                                if trans_data["packet_number"] == 1 \
                                and os.path.isfile(file_path):
                                    Logger.PrintLog(LOG_INFO, "Existing file for {} has found. Deleting it before writing the new packet."
                                                    .format(data_str))
                                    os.remove(file_path)

                                with open(file_path, file_mode) as f:
                                    f.write(trans_data["data"])

                                Logger.PrintLog(LOG_INFO, "Recieved data has successfully saved to {}."
                                                .format(file_path))
                            else:
                                Logger.PrintLog(LOG_INFO, "Recieved data has successfully saved to memory."
                                                .format(file_path))

                                cls.set_packet_data(telemetry.Packet.Type.Special.TRANS_DATA,
                                                    {data_str: trans_data["data"]})

                            cls.send(telemetry.Packet.Message.prepare(telemetry.Packet.Data.Response.SUCCESS))
                            Logger.PrintLog(
                                LOG_INFO, "Recieved valid data packet. Chunk count: {}, Packet number: {}, Data size: {}, Data str: {}, File mode: {}."
                                .format(str(trans_data["chunk_count"]),
                                        str(trans_data["packet_number"]),
                                        str(trans_data["data_size"]),
                                        data_str,
                                        str(file_mode)))
                        continue
                    # .\if packet_type == telemetry.Packet.Type.DATA_TRANSMISSION
                if callable(cls._handler):
                    cls._handler(cls)
            except Exception as ex:
                cls.exception_handler(__file__, ex)

    # Public Method(s)
    def get_status(self) -> bool:
        if self._status == 1: return True

        return False

    def set_handler(self,
                    func: Callable):
        if callable(func):
            self._handler = func

    def connect(self) -> None:
        LOG_INFO = "tcp_client.py - connect()"

        # if not callable(self._handler):
        #     Logger.PrintLog(LOG_INFO, "self.handler is not callable.")
        #     return

        if self._type == TCP_Client.Type.UNSPECIFIED:
            self.set_type(TCP_Client.Type.RECV_ONLY)

        self._socket.connect((self._ip, self._port))

        self._status = 1

        if  self._type != TCP_Client.Type.RECV_ONLY \
        and self._type != TCP_Client.Type.SEND_AND_RECV:
            Logger.PrintLog(LOG_INFO, "Client type is not eligible for receiving data. Handler thread is not going to started.")
            return

        t = threading.Thread(target=self._thread_handler, args=(self,))
        t.daemon = False
        t.start()

    def stop(self) -> None:
        if self._status == 1:
            self._status = 2
            self._socket.close()

    def send(self,
             data   : bytes,
             timeout: bool = False) -> None:
        LOG_INFO = "tcp_client.py - send()"

        if  self._type != TCP_Client.Type.SEND_ONLY \
        and self._type != TCP_Client.Type.SEND_AND_RECV:
            Logger.PrintLog(LOG_INFO, "Client type is not eligible for sending data.")
            return

        self.delete_packet_data(telemetry.Packet.Type.MESSAGE)

        if timeout: self._socket.settimeout(self.get_write_timeout())

        self._socket.send(data)

    def set_type(self,
                 client_type: int) -> None:
        if  client_type != TCP_Client.Type.UNSPECIFIED \
        and client_type != TCP_Client.Type.RECV_ONLY   \
        and client_type != TCP_Client.Type.SEND_ONLY   \
        and client_type != TCP_Client.Type.SEND_AND_RECV:
            return

        self._type = client_type

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
                        packet_type: int,
                        data       : any,
                        append_mode: bool = False) -> None:
        if not self.get_is_packet_type_exist(packet_type): self._data[packet_type] = None

        if append_mode:
            self._data[packet_type] = self._data[packet_type] + data
            return

        self._data[packet_type] = data

    def get_packet_data(self,
                        packet_type: int,
                        extract    : bool = False) -> any:
        if not self.get_is_packet_type_exist(packet_type): return None

        data = self._data[packet_type]

        if extract:
            try:
                return telemetry.Packet.get_class_by_type(packet_type).extract(data)
            except AttributeError:
                Logger.PrintLog(self.LOG_INFO, "get_packet_data() - [WARNING] - Packet type ({}) doesn't have extract method."
                                .format(str(packet_type)))

        return data

    def clear_packet_data(self,
                          packet_type: int) -> None:
        if not self.get_is_packet_type_exist(packet_type): return

        self._data[packet_type] = None

    def delete_packet_data(self,
                          packet_type: int) -> None:
        if not self.get_is_packet_type_exist(packet_type): return

        del self._data[packet_type]

    def get_is_packet_type_exist(self,
                                 packet_type: int) -> bool:
        if packet_type in self._data: return True

        return False

    def set_last_packet_type(self,
                             packet_type: int) -> None:
        self._storage["last_packet_type"] = packet_type

    def get_last_packet_type(self) -> int:
        return self._storage["last_packet_type"]

    def get_failure_tracker(self) -> any:
        return self._storage["failure_tracker"]

    def set_variable(self,
                     key: str,
                     val: any) -> None:
        self._storage["variable_list"][key] = val

    def get_variable(self,
                     key: str) -> any:
        if not key in self._storage["variable_list"]: return None

        return self._storage["variable_list"][key]

    def set_name(self,
                 name: str):
        self._name = name

    def get_name(self):
        return self._name

    def exception_handler(self,
                          file: str,
                          ex  : Exception) -> None:
        self._status = 0

        file = file.split("\\")[-1].split("/")[-1]
        LOG_INFO = "tcp_client.py - exception_handler() - called by "+file
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
