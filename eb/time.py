"""
    Author: Ege Bilecen
    Date  : 24.07.2020
"""
from datetime import datetime

class Time:
    @staticmethod
    def get_current_timestamp(time_type: str = "sec") -> int:
        if time_type == "ms":
            return int(datetime.now().timestamp() * 1000)

        return int(datetime.now().timestamp())

    @staticmethod
    def get_current_date() -> str:
        return datetime.now().strftime("%d/%m/%Y")

    @staticmethod
    def get_current_clock(micro_seconds: bool = False) -> str:
        date_format = "%H:%M:%S"

        if micro_seconds: date_format += ".%f"

        return datetime.now().strftime(date_format)
