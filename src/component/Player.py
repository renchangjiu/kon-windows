from PyQt5.QtCore import QObject, QProcess

from src.component.Constant import Constant


class Player(QObject):
    state_empty = -1
    state_playing = 1
    state_paused = 2
    state_stop = 3

    def __init__(self) -> None:
        super().__init__()

        # 音量
        self.__volume = 50

        # 是否静音
        self.__mute = False

        # 音乐文件路径
        self.__path = ""

        self.process = QProcess(self)

        self.state = self.state_empty

    def prepare(self, path: str):
        self.__path = path
        self.state = self.state_stop

    def start(self):
        """ 开始或继续播放。如果以前已暂停播放，则将从暂停的位置继续播放。如果播放已停止或之前从未开始过，则播放将从头开始。"""
        if self.state == self.state_paused:
            pass
        elif self.state == self.state_stop:
            cmd = Constant.res + "/lib/mplayer.exe -slave -quiet -volume %d \"%s\"" % (self.__volume, self.__path)
            pass

    def pause(self):
        pass

    def volume(self, vol=-1) -> int:
        """ 获取或设置音量/
        :param vol:
        """
        if vol >= 0:
            self.__volume = vol
        return self.__volume

    def mute(self, mute=-1) -> bool:
        """获取或设置静音状态.

        :param mute: 若为1, 则设置为静音; 若为0, 则设置为非静音; 若为-1, 则获取静音状态
        """
        if mute == 1:
            self.__mute = True
        elif mute == 0:
            self.__mute = False
        return self.__mute

    def playing(self):
        pass

    def position(self):
        # 获取当前播放进度
        pass

    def duration(self):
        pass
