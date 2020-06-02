from PyQt5.QtCore import QObject


class Player(QObject):

    def __init__(self) -> None:
        super().__init__()
        self.__volume = 50
        self.__mute = False

    def prepare(self):
        pass

    def start(self):
        """ 开始或继续播放。如果以前已暂停播放，则将从暂停的位置继续播放。如果播放已停止或之前从未开始过，则播放将从头开始。"""
        pass

    def pause(self):
        pass

    def volume(self, vol=-1):
        """ 获取或设置音量 """
        pass

    def mute(self):
        pass

    def playing(self):
        pass
