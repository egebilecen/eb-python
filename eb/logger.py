"""
    Author: Ege Bilecen
    Date  : 22.07.2020
"""
from os       import path as os_path
from datetime import datetime

import config

class Logger:
    LOG_FILE_OVERRIDE = None

    @staticmethod
    def PrintLog(LOG_INFO     : str,
                 text         : str,
                 write_to_file: bool = True):
        if config.Logger.ENABLED:
            date = "["+datetime.now().strftime("%d/%m/%Y - %H:%M:%S")+"]"

            print_text = date + " - [" + LOG_INFO + "] - " + text

            print(print_text)

            if write_to_file:
                if Logger.LOG_FILE_OVERRIDE is None:
                    LOG_FILE = config.Logger.LOG_FILE
                else:
                    LOG_FILE = Logger.LOG_FILE_OVERRIDE

                LOG_FILE = config.Logger.OUTPUT_DIR + LOG_FILE

                if os_path.exists(LOG_FILE): write_mode = "a"
                else: write_mode = "w"

                with open(LOG_FILE, write_mode) as f:
                    f.write(print_text+"\n")

    @classmethod
    def PrintException(cls,
                       LOG_INFO     : str,
                       ex           : Exception,
                       write_to_file: bool = True):
        cls.PrintLog(LOG_INFO, "{} - {}".format(type(ex).__name__, str(ex)), write_to_file)
