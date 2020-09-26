"""
    Author: Ege Bilecen
    Date  : 18.08.2020
"""
from typing import Callable, Optional
from time   import sleep
import threading

from eb.time import Time

class Method:
    @staticmethod
    def execute_in_background(func : Callable,
                              args : tuple):
        status_dict = {
            "completed"  : False,
            "return_val" : None
        }

        _ = threading.Thread(target=func, args=(status_dict,)+args)
        _.daemon = False
        _.start()

        return status_dict

    class Repeat:
        """
            Repeat a function for X times.

            Return (True, RET_VAL) if function returns RET_VAL in any attempts.
            Return (False, None) if function doesn't return RET_VAL in all attempts.
        """
        @staticmethod
        def until_value(func           : Callable,
                        args           : tuple,
                        repeat_count   : int,
                        repeat_delay_ms: Optional[int] = None,
                        ret_val        : any           = True) -> tuple:
            if repeat_count < 1: raise ValueError("repeat_count < 1")

            if  repeat_delay_ms is not None \
            and repeat_delay_ms <= 0: raise ValueError("delay <= 0")

            i = 0

            while i != repeat_count:
                if  repeat_delay_ms is not None \
                and i > 0: sleep(repeat_delay_ms / 1000)

                try:
                    res = func(*args)

                    if res == ret_val: return True, ret_val
                    else:
                        i += 1
                        continue
                except:
                    i += 1
                    continue

            return False, None

        @staticmethod
        def until_value_not(func           : Callable,
                            args           : tuple,
                            repeat_count   : int,
                            repeat_delay_ms: Optional[int] = None,
                            ret_val        : any           = True) -> tuple:
            if repeat_count < 1: raise ValueError("repeat_count < 1")

            if  repeat_delay_ms is not None \
            and repeat_delay_ms <= 0: raise ValueError("delay <= 0")

            i = 0

            while i != repeat_count:
                if  repeat_delay_ms is not None \
                and i > 0: sleep(repeat_delay_ms / 1000)

                try:
                    res = func(*args)

                    if res != ret_val:
                        return True, res
                    else:
                        i += 1
                        continue
                except:
                    i += 1
                    continue

            return False, None

        @staticmethod
        def x_times(func        : Callable,
                    args        : tuple,
                    repeat_count: int,
                    repeat_delay_ms: Optional[int] = None) -> None:
            if repeat_count < 1: raise ValueError("repeat_count < 1")

            if  repeat_delay_ms is not None \
            and repeat_delay_ms <= 0: raise ValueError("delay <= 0")

            for i in range(repeat_count):
                func(*args)

                if repeat_delay_ms is not None:
                    sleep(repeat_delay_ms / 1000)

    class Wait:
        @staticmethod
        def until_value(func           : Callable,
                        args           : tuple,
                        timeout        : int           = 0,
                        repeat_delay_ms: Optional[int] = None,
                        ret_val        : any           = True) -> None:
            if  repeat_delay_ms is not None \
            and repeat_delay_ms <= 0: raise ValueError("delay <= 0")

            start_time = Time.get_current_timestamp("ms")

            while timeout == 0 \
            or    Time.get_current_timestamp("ms") - start_time < timeout:
                if func(*args) == ret_val: return

                if repeat_delay_ms is not None:
                    sleep(repeat_delay_ms / 1000)

            raise TimeoutError

    class Dict:
        # timeout_ms - 0 means no timeout.
        @staticmethod
        def wait_until_value(dictionary: dict,
                             key       : str,
                             value     : any,
                             timeout_ms: int = 10000) -> None:
            if timeout_ms < 0: raise ValueError("Timeout < 0.")

            start_timestamp = Time.get_current_timestamp("ms")

            while timeout_ms == 0 \
            or    Time.get_current_timestamp("ms") - start_timestamp <= timeout_ms:
                if key not in dictionary:    continue
                if dictionary[key] == value: return

            raise TimeoutError
