from src.component.Constant import Constant


class Test(object):
    @staticmethod
    def init():
        Constant.root = "C:/GitHub/kon-windows"
        Constant.data = Constant.root + "/data"
        Constant.res = Constant.root + "/resource"


if __name__ == "__main__":
    pass
