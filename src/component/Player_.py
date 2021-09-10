import re

from PyQt5.QtCore import QObject, QProcess, QTimer

from src.component.Const import Const


class Player(QObject):
    state_idle = -1
    state_prepared = 1
    state_playing = 2
    state_paused = 3

    __duration_ptn = re.compile("ANS_LENGTH=(.*?)\\\\r")
    __position_ptn = re.compile("ANS_TIME_POSITION=(.*?)\\\\r")

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
        self.__process.readyReadStandardOutput.connect(self.__read_standard_output)
        self.__process.readyReadStandardError.connect(self.__read_error_output)

        # 播放状态
        self.__state = self.state_idle

        # 当前播放进度, 单位: 毫秒
        self.__position = 0

        # 时长, 单位: 毫秒
        self.__duration = 0

        # 定时器, 每隔0.1s 使 mplayer 输出时间信息(duration & position)
        self.timer = QTimer(self)
        self.timer.start(100)
        self.timer.timeout.connect(self.__get_info)

    def prepare(self, path: str):
        self.__path = path
        self.__state = self.state_prepared
        return self

    def start(self):
        """ 开始或继续播放。如果以前已暂停播放，则将从暂停的位置继续播放。如果播放已停止或之前从未开始过，则播放将从头开始。"""
        if self.__state == self.state_paused:
            self.__process.write(b"pause\n")
            self.__state = self.state_playing
        elif self.__state == self.state_prepared:
            cmd = Const.res + "/lib/mplayer.exe -slave -quiet -volume %d \"%s\"" % (self.__volume, self.__path)
            self.__process.start(cmd)
            self.__process.write(b"get_time_length\n")
            self.__state = self.state_playing
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
            self.__mute = mute
            self.__process.write(b"mute 1\n")
        else:
            self.__mute = mute
            self.__process.write(b"mute 0\n")
        return self.__mute

    def playing(self) -> bool:
        """ 当前是否处于播放状态。 """
        return self.__state == self.state_playing

    def seek(self, position: int):
        """ 跳跃到指定的时间位置。
        :param position: 绝对时间位置, 毫秒。
        """
        self.__process.write(b"seek %.1f 2\n" % (position / 1000))

    def listen(self, callback):
        """ 设置播放结束的回调方法 """
        self.__complete_callback = callback

    def position(self) -> int:
        """ 获取当前播放进度。 """
        return self.__position

    def duration(self) -> int:
        """ 获取时长。 """
        return self.__duration

    def __get_info(self):
        if self.__state == self.state_playing:
            self.__process.write(b"get_time_pos\n")

    def __read_standard_output(self):
        while self.__process.canReadLine():
            output = str(self.__process.readLine())
            print(output)
            self.__parse_output(output)

    def __parse_output(self, output: str):
        position_match = self.__position_ptn.search(output)
        # 处理播放位置
        if position_match is not None:
            self.__position = int(float(position_match.group(1))) * 1000
            return
        duration_match = self.__duration_ptn.search(output)
        # 处理时长
        if duration_match is not None:
            self.__duration = int(float(duration_match.group(1))) * 1000
            return
        # 处理结束事件
        if output.find("Exiting... (End of file)") != -1:
            print("当前歌曲播放结束")
            self.__state = self.state_idle
            self.__path = ""
            if self.__complete_callback is not None:
                self.__complete_callback()
            return

    def __read_error_output(self):
        while self.__process.canReadLine():
            line = self.__process.readLine()
            print(line)
