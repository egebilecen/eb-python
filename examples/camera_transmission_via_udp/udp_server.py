import struct
import hashlib
import cv2

from eb.udp_server             import UDP_Server
from eb.image_processing.image import Image

last_camera_frame_timestamp = 0
last_camera_frame = None

def data_handler(addr, data):
    global last_camera_frame_timestamp
    global last_camera_frame

    if  data[:2]  != b"\x7C\xA3" \
    and data[-2:] != b"\x58\x10":
        return

    timestamp = struct.unpack("<Q", data[2:10])[0]
    md5       = data[10:26]
    frame_len = struct.unpack("<I", data[26:30])[0]
    frame     = data[30:-2]

    if timestamp < last_camera_frame_timestamp: return
    if frame_len != len(frame):                 return
    if md5 != hashlib.md5(frame).digest():      return

    last_camera_frame_timestamp = timestamp
    last_camera_frame           = Image.Decode.FromEncodedImage(frame)

server = UDP_Server("192.168.1.8", 3630, is_async = True, buffer_size = 1 * 1024 * 1024, is_logging_enabled = False)
server.set_data_handler(data_handler)
server.run()

while 1:
    if last_camera_frame is not None:
        cv2.imshow("UDP Client Camera Frame", last_camera_frame)
        cv2.waitKey(1)

cv2.destroyAllWindows()
