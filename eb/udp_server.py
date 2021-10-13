import socket
import threading
from time import time, sleep

from eb.logger import Logger

class UDP_Server:
    _server_addr             = ("", 6969)
    _socket                  = None
    _buffer_size             = 512

    _server_ping_interval_ms = 3000
    _client_timeout_ms       = 5000

    _socket_list             = {}
    _async                   = False

    def __init__(self,
                 ip                 = "192.168.1.2",
                 port               = 6969,
                 buffer_size        = 512,
                 is_async           = False,
                 is_logging_enabled = True):
        self._server_addr = (ip, port)
        self._async       = is_async
        self._buffer_size = buffer_size

        Logger.LOGGING_ENABLED = is_logging_enabled

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind(self._server_addr)

    @staticmethod
    def _ping(udp_server):
        Logger.PrintLog("UDP SERVER", "[?] UDP Server ping thread has started.")

        while 1:
            socket_list = udp_server._socket_list.copy()
            delete_list = []

            for client_addr in socket_list:
                client_time_data = socket_list[client_addr]

                if (int(time()) - client_time_data["last_ping"]) * 1000 >= udp_server._server_ping_interval_ms:
                    try:
                        # Logger.PrintLog("UDP SERVER", "Sending ping to {}:{}.".format(client_addr[0], client_addr[1]))
                        udp_server._socket.sendto(b"ping", client_addr)
                    except Exception as ex: 
                        Logger.PrintException("UDP SERVER - PING THREAD", ex)
                    
                    udp_server._socket_list[client_addr]["last_ping"] = int(time())
                
                if  client_time_data["last_activity"] == 0:
                    if (int(time()) - client_time_data["connected"]) * 1000 >= udp_server._client_timeout_ms + udp_server._server_ping_interval_ms:
                        delete_list.append(client_addr)
                elif (int(time()) - client_time_data["last_activity"]) * 1000 >= udp_server._client_timeout_ms:
                    delete_list.append(client_addr)

            for client_addr in delete_list:
                Logger.PrintLog("UDP SERVER", "[!] {}:{} has been timeouted.".format(client_addr[0], client_addr[1]))
                del udp_server._socket_list[client_addr]

        Logger.PrintLog("UDP SERVER", "[!] UDP Server ping thread has ended.")

    def run(self):
        def impl(udp_server):
            ping_thread = threading.Thread(target=UDP_Server._ping, args=(self,), daemon=True)
            ping_thread.start()

            Logger.PrintLog("UDP SERVER", "[?] UDP Server listening for connections.")

            while 1:
                try:
                    data, addr = udp_server._socket.recvfrom(udp_server._buffer_size)
                except ConnectionResetError and ConnectionAbortedError and ConnectionError as ex:
                    Logger.PrintException("UDP SERVER", ex)
                    continue

                Logger.PrintLog("UDP SERVER", "{}:{} sent {} bytes long data: {}".format(addr[0], addr[1], len(data), " ".join("0x{:02x}".format(elem) for elem in data)))

                if addr not in udp_server._socket_list:
                    Logger.PrintLog("UDP SERVER", "[?] {}:{} has connected to server.".format(addr[0], addr[1]))

                    connect_time = int(time())

                    udp_server._socket_list[addr] = {
                        "connected"     : connect_time,
                        "last_activity" : 0,
                        "last_ping"     : connect_time
                    }
                elif data == b"pong":
                    # Logger.PrintLog("UDP SERVER", "Received pong from {}:{}.".format(addr[0], addr[1]))
                    udp_server._socket_list[addr]["last_activity"] = int(time())

        if not self._async:
            impl(self)
        else:
            server_thread = threading.Thread(target=impl, args=(self,), daemon=True)
            server_thread.start()

    def publish_data(self, byte_data):
        for client_addr in self._socket_list:
            self._socket.sendto(byte_data, client_addr)
