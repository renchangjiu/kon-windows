from PyQt5.QtCore import QObject, QProcess

from src.component.Constant import Constant


class Player(QObject):
    state_idle = -1
    state_prepared = 1
    state_playing = 2
    state_paused = 3

    def __init__(self) -> None:
        super().__init__()

        # 音量
        self.__volume = 50

        # 是否静音
        self.__mute = False

        # 音乐文件路径
        self.__path = ""

        # 播放结束的回调方法
        self.__complete_callback = None

        # 负责操作 mplayer
        self.__process = QProcess(self)

        # 播放状态
        self.__state = self.state_idle

        # 当前播放进度
        self.__position = -1

        # 时长
        self.__duration = -1

    def prepare(self, path: str):
        self.__path = path
        self.__state = self.state_prepared
        return self

    def start(self):
        """ 开始或继续播放。如果以前已暂停播放，则将从暂停的位置继续播放。如果播放已停止或之前从未开始过，则播放将从头开始。"""
        if self.__state == self.state_paused:
            self.__process.write(b"pause\n")
        elif self.__state == self.state_prepared:
            cmd = Constant.res + "/lib/mplayer.exe -slave -quiet -volume %d \"%s\"" % (self.__volume, self.__path)
            self.__process.start(cmd)
            self.__process.readyReadStandardOutput.connect(self.read_standard_output)
            self.__process.readyReadStandardError.connect(self.read_standard_error)
        return self

    def pause(self):
        """ 暂停播放 """
        if self.__state == self.state_playing:
            self.__process.write(b"pause\n")
            self.__state = self.state_paused

    def stop(self):
        self.__process.write(b"quit 1")
        self.__process.kill()
        self.__state = self.state_idle

    def read_standard_output(self):
        pass

    def read_standard_error(self):
        pass

    def volume(self, vol=-1) -> int:
        """ 获取或设置音量
        :param vol:
        """
        if 0 <= vol <= 0:
            self.__volume = vol
            self.__process.write(b"volume %d 50\n" % vol)
        return self.__volume

    def mute(self, mute=None) -> bool:
        """获取或设置静音状态.

        :param mute: 若为 true, 则设置为静音; 若为 false, 则设置为非静音;
        """
        if mute:
            self.__mute = True
            self.process.write(b"mute 1\n")
        elif mute:
            self.__mute = False
            self.process.write(b"mute 0\n")
        return self.__mute

    def playing(self) -> bool:
        """ 当前是否处于播放状态 """
        return self.__state == self.state_playing

    def listen(self, callback):
        """ 设置播放结束的回调方法 """
        self.__complete_callback = callback

    def position(self):
        # 获取当前播放进度
        return self.__position

    def duration(self):
        # 获取时长
        return self.__duration
