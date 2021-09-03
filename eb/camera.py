"""
    Author: Ege Bilecen
    Date  : 22.07.2020
"""
from time import sleep
import cv2
import threading

from eb.logger import Logger
from eb.image_processing.image import Image

class Camera:
    def __init__(self,
                 device      : int   = 0,
                 resolution  : tuple = (640, 480),
                 fps         : int   = 30,
                 file_name   : str   = "",
                 output_dir  : str   = "./video_output/",
                 frame_encode: str   = ".jpg") -> None:
        self._last_frame   = b""
        self._status       = 0
        self._device       = device
        self._resolution   = resolution
        self._fps          = fps
        self._file_name    = file_name
        self._output_dir   = output_dir
        self._frame_encode = frame_encode

        self._camera     = None
        self._writer     = None

        self.LOG_INFO    = "camera.py - "

    # Private Method(s)
    @staticmethod
    def _thread_handler(cls) -> None:
        LOG_INFO = cls.LOG_INFO+"_thread_handler() - "

        while cls._status:
            if cls._camera.isOpened():
                try:
                    _, frame = cls._camera.read()

                    if cls._writer is not None:
                        cls._writer.write(frame)

                    cls._last_frame = frame
                except Exception as ex:
                    Logger.PrintException(LOG_INFO, ex)
                    sleep(0.1)
            else:
                Logger.PrintLog(LOG_INFO, "Camera is not open. Terminating the thread.")
                cls._status = 0
                break

        cls._camera.release()

        if cls._writer is not None:
            cls._writer.release()

    # Public Method(s)
    def start(self) -> None:
        Logger.PrintLog(self.LOG_INFO+"start()", "Starting the camera. (Device ID: {})".format(self._device))
        
        self._camera = cv2.VideoCapture(self._device)

        if self._file_name != "":
            codec = cv2.VideoWriter_fourcc("X", "V", "I", "D")
            self._writer = cv2.VideoWriter(self._output_dir + self._file_name+".avi", codec, self._fps / 4, self._resolution)

        self._camera.open(self._device)

        self._status = 1

        t = threading.Thread(target=self._thread_handler, args=(self,))
        t.daemon = False
        t.start()

        Logger.PrintLog(self.LOG_INFO+"start()", "Camera should have been started.")

    def stop(self) -> None:
        Logger.PrintLog(self.LOG_INFO+"stop()", "Stopping the camera.")
        self._status = 0

    def get_last_frame(self,
                       raw_frame: bool = False) -> bytes:
        if not raw_frame:
            return Image.Encode.FromRawImage(self._last_frame, self._frame_encode)

        return self._last_frame
