"""
    Author: Ege Bilecen
    Date  : 22.07.2020
"""
import traceback
from os       import path as os_path
from datetime import datetime

class Logger:
    LOG_FILE = "./eb.log"
    LOGGING_ENABLED = True

    @staticmethod
    def PrintLog(title        : str,
                 text         : str,
                 write_to_file: bool = True):
        if Logger.LOGGING_ENABLED:
            date = "["+datetime.now().strftime("%d/%m/%Y - %H:%M:%S")+"]"

            print_text = date + " - [" + title + "] - " + text

            print(print_text)

            if write_to_file:
                if os_path.exists(Logger.LOG_FILE): write_mode = "a"
                else: write_mode = "w"

                with open(Logger.LOG_FILE, write_mode) as f:
                    f.write(print_text+"\n")

    @classmethod
    def PrintException(cls,
                       title        : str,
                       ex           : Exception,
                       write_to_file: bool = True):
        cls.PrintLog(title, "{}\n{}".format(type(ex).__name__, traceback.format_exc()), write_to_file)
