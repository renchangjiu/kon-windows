import json
import sys
from typing import List, Type

from src.component.Apps import Apps
from src.component.config.ScannedPath import ScannedPath


class Config(object):

    def __init__(self) -> None:
        """读取 config.json 文件, 实例化配置类"""
        # file = open(Apps.data_path + "/config.json", "r", encoding="utf-8")
        file = open("C:/GitHub/kon-windows/data/config.json", "r", encoding="utf-8")
        obj = json.loads(file.read())
        file.close()
        self.scanned_paths = self.__parse_sp(obj["scannedPaths"])

    def __parse_sp(self, sps: list) -> list:
        print(sps)
        res = []
        for sp in sps:
            path = ScannedPath()
            path.path = sp["path"]
            path.checked = sp["checked"]
            res.append(path)
        return res

    @staticmethod
    def save():
        pass


if __name__ == "__main__":
    Apps.init(sys.argv)
    config = Config()
    pass
