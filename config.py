"""
    Author: Ege Bilecen
    Date  : 21.07.2020
"""
from os.path    import expanduser
from eb.convert import Convert

"""
    EB Library Defines
"""
BASE_DIR = expanduser("~/epl_drone/")

class Logger:
    ENABLED    = 1
    LOG_FILE   = "eb.log"
    OUTPUT_DIR = BASE_DIR + "logs/"

class Connection:
    TARGET_IP   = "192.168.1.2"
    TARGET_PORT = {
        "data"      : 6969, # data transmission (e.g. video file)
        "camera"    : 6970,
        "telemetry" : 6971
    }
    BUFFER_SIZE   = Convert.megabytes_to_bytes(5)
    CONNECT_DELAY = 2

class Camera:
    DEVICE_INDEX = 0
    RESOLUTION   = (640, 480)
    FPS          = 30
    FRAME_ENCODE = ".jpg"
    OUTPUT_DIR   = BASE_DIR
