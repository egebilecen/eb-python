from time import sleep

from matplotlib.pyplot import imshow

from eb.camera     import Camera
from eb.udp_client import UDP_Client
from eb.time       import Time

import struct
import hashlib

def prepare_camera_frame_packet(frame : bytes) -> bytes:
    frame_md5 = hashlib.md5(frame).digest()
    frame_len = len(frame)

    # Packet structure:
    # \x7C\xA3<timestamp (long)><frame md5 checksum (16 bytes)><frame len (unsigned long)><frame (x len)>\x58\x10
    packet = bytearray()
    packet.extend(b"\x7C\xA3")
    packet.extend(struct.pack("<Q", Time.get_current_timestamp("ms")))
    packet.extend(frame_md5)
    packet.extend(struct.pack("<I", frame_len))
    packet.extend(frame)
    packet.extend(b"\x58\x10")

    return bytes(packet)

client = UDP_Client("192.168.1.8", 3630, is_logging_enabled = False)
client.connect()
client.send(b"")

FPS = 60
camera = Camera(fps = FPS)
camera.start()
sleep(2)

while 1:
    try:
        frame = camera.get_last_frame(True)
    except ValueError: continue

    packet = prepare_camera_frame_packet(frame)
    client.send_chunked(packet)
    
    sleep(1 / FPS)
