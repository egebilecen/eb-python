import socket
import threading

from eb.logger import Logger

class UDP_Client:
    _server_addr = None
    _socket      = None
    _buffer_size = 512

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
                elif callable(self._data_callback):
                    self._data_callback(self, data)

        _ = threading.Thread(target=impl, args=(self,))
        _.daemon = True
        _.start()

    def set_variable(self, key, val):
        self._variables[key] = val

    def get_variable(self, key):
        return self._variables[key]

    def send(self, byte_data):
        self._socket.sendto(byte_data, self._server_addr)
