from src.component.Const import Const


class Test(object):
    @staticmethod
    def init():
        Const.root = "D:/su/GitHub/kon-windows"
        Const.data = Const.root + "/data"
        Const.res = Const.root + "/resource"


if __name__ == "__main__":
    pass
