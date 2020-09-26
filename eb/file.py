"""
    Author: Ege Bilecen
    Date  : 19.08.2020
"""
from typing import List, Optional
import os

class File:
    @staticmethod
    def get_directory_content(path: str) -> List[str]:
        return os.listdir(path)

    @staticmethod
    def get_file_list(path:str, sort: Optional[str] = None) -> List[str]:
        if path[-1] != "/": path += "/"

        dir_content = File.get_directory_content(path)
        file_list   = [elem for elem in dir_content if os.path.isfile(path+elem)]

        if sort == "alphabetically":
            return sorted(file_list, key=str.lower)

        return file_list
