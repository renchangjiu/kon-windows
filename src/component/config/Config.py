import json

from src.component.Constant import Constant
from src.component.config.ScannedPath import ScannedPath


class Config(object):

    def __init__(self) -> None:
        """读取 config.json 文件, 实例化配置类"""
        self.scanned_paths = []
        self.__config_path = ""

    def init(self):
        """ 将配置文件解析为配置对象 """
        self.__config_path = Constant.data + "/config.json"
        file = open(self.__config_path, "r", encoding="utf-8")
        json_obj = json.loads(file.read())
        file.close()
        self.scanned_paths = ScannedPath.parse(json_obj)

    def save(self):
        """将配置对象转换为 JSON 字符串, 并写入磁盘"""
        obj = {
            "scannedPaths": ScannedPath.stringify(self.scanned_paths)
        }
        json_str = json.dumps(obj, ensure_ascii=False)
        file = open(self.__config_path, "w", encoding="utf-8")
        file.write(json_str)
        file.close()
