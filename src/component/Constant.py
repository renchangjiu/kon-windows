import os
import sys


class Constant(object):
    """ 维护应用运行的基本参数 """

    # 应用根目录, 如: D:/su/GitHub/kon-windows
    root = ""

    # 数据库文件目录, 如: D:/su/GitHub/kon-windows/data
    data = ""

    # 资源文件目录, D:/su/GitHub/kon-windows/resource
    res = ""

    @classmethod
    def init(cls, argv):
        cls.root = os.path.split(os.path.abspath(argv[0]))[0].replace("\\", "/")
        cls.data = cls.root + "/data"
        cls.res = cls.root + "/resource"
