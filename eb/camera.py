"""
    Author: Ege Bilecen
    Date  : 22.07.2020
"""
from time   import sleep
from typing import Union
from numpy  import ndarray
import cv2
import threading

from eb.logger import Logger
from eb.image_processing.image import Image

class Camera:
    def __init__(self,
                 device      : int             = 0,
                 resolution  : tuple[int, int] = (640, 480),
                 fps         : int             = 30,
                 file_name   : str             = "",
                 output_dir  : str             = "./video_output/",
                 frame_encode: str             = ".jpg") -> None:
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
        t.daemon = True
        t.start()

        Logger.PrintLog(self.LOG_INFO+"start()", "Camera should have been started.")

    def stop(self) -> None:
        Logger.PrintLog(self.LOG_INFO+"stop()", "Stopping the camera.")
        self._status = 0

    def display(self) -> None:
        if not self._status:
            raise Exception("Camera is not started.")

        while 1:
            last_frame = self.get_last_frame(frame_encode = False)

            if last_frame == b"": continue

            cv2.imshow("Camera (Device ID: {}, Resolution: {}x{})".format(self._device, self._resolution[0], self._resolution[1]), last_frame)
            if cv2.waitKey(1) == 27: break

        cv2.destroyAllWindows()

    def get_last_frame(self,
                       frame_encode: bool = False,
                       mirror      : bool = True) -> Union[bytes, ndarray]:
        last_frame = self._last_frame

        if last_frame != b"":
            if mirror:
                last_frame = cv2.flip(last_frame, 1)

            if frame_encode:
                if last_frame == b"":
                    raise ValueError("Last frame is empty! Cannot encode it.")

                # Returns bytes
                return Image.Encode.FromRawImage(last_frame, self._frame_encode)

            # Returns numpy.ndarray or bytes if frame is empty
            return last_frame

        return b""
