import socket
import threading
import struct
import hashlib

from math import ceil

from eb.logger import Logger
from eb.udp_server import UDP_Server

class UDP_Client:
    MAX_DATA_SIZE = 65535 - 8 - 20

    CHUNKED_DATA_START_BYTES = b"\x6E\x62"
    CHUNKED_DATA_END_BYTES   = b"\x52\xE3"
    CHUNKED_DATA_PACKET_SIZE = len(CHUNKED_DATA_START_BYTES) + 18 + len(CHUNKED_DATA_END_BYTES)

    _server_addr  = None
    _socket       = None
    _buffer_size  = 512

    def __init__(self, 
                 server_ip,
                 server_port,
                 buffer_size        = 512,
                 is_logging_enabled = True):
        self._server_addr   = (server_ip, server_port)
        self._buffer_size   = buffer_size
        self._data_callback = None
        self._variables     = {}

        Logger.LOGGING_ENABLED = is_logging_enabled

    @staticmethod
    def prepare_chunked_data_packet(total_chunks, chunk_id, byte_data):
        # Format: <start bytes><total chunks><chunk id><md5 checksum of data><data><end bytes>
        # Packet format length (without byte data and start/end bytes): 
        # 1 total chunks + 1 chunk id + 16 md5 = 18 bytes
        packet = bytearray()
        packet.extend(UDP_Client.CHUNKED_DATA_START_BYTES)
        packet.extend(struct.pack("<B", total_chunks))
        packet.extend(struct.pack("<B", chunk_id))
        packet.extend(hashlib.md5(byte_data).digest())
        packet.extend(byte_data)
        packet.extend(UDP_Client.CHUNKED_DATA_END_BYTES)

        return packet

    def set_data_callback(self, func):
        if callable(func):
            self._data_callback = func

    def connect(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind(("", 0))

        def impl(client_socket):
            while 1:
                try:
                    data, server_addr = client_socket._socket.recvfrom(client_socket._buffer_size)
                except ConnectionResetError:
                    Logger.PrintLog("UDP CLIENT", "Couldn't connect to server. Is server online? (CONNECTION RESET ERROR)")
                    return

                Logger.PrintLog("UDP CLIENT", "Recieved {} bytes long data: {}".format(len(data), " ".join("0x{:02x}".format(elem) for elem in data)))

                if data == b"ping":
                    Logger.PrintLog("UDP CLIENT", "Received ping, sending pong.")
                    client_socket.send(b"pong")
                elif self._data_callback is not None:
                    self._data_callback(self, data)

        _ = threading.Thread(target=impl, args=(self,))
        _.daemon = True
        _.start()

    def set_variable(self, key, val):
        self._variables[key] = val

    def get_variable(self, key):
        return self._variables[key]

    def send(self, byte_data):
        if len(byte_data) > self.MAX_DATA_SIZE:
            raise OverflowError("Max. data length cannot exceed {} bytes. Please use send_chunked() method instead.".format(self.MAX_DATA_SIZE))

        self._socket.sendto(byte_data, self._server_addr)

    def send_chunked(self, byte_data):
        chunk_data_size = self.MAX_DATA_SIZE - self.CHUNKED_DATA_PACKET_SIZE
        chunk_count     = ceil(len(byte_data) / chunk_data_size)

        for i in range(chunk_count):
            chunked_data   = byte_data[chunk_data_size * i : chunk_data_size * (i + 1)]
            chunked_packet = UDP_Client.prepare_chunked_data_packet(chunk_count, i + 1, chunked_data)
            self.send(chunked_packet)
