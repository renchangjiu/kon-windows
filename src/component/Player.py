from threading import Lock

from PyQt5 import QtCore
from PyQt5.QtCore import QObject, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer

from src.util.Commons import Commons


class Player(QObject):
    state_idle = -1
    state_prepared = 1
    state_playing = 2
    state_paused = 3

    # 信号: 当音量变化时, 参数为当前音量.
    volumeChanged = QtCore.pyqtSignal(int)

    # 信号: 当播放位置变化时, 参数为当前位置
    positionChanged = QtCore.pyqtSignal(int)

    # 信号: 当播放状态变化时, 参数为当前状态
    stateChanged = QtCore.pyqtSignal(int)

    # 信号: 当静音状态变化时, 参数为当前状态
    mutedChanged = QtCore.pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()
        self.__path = None
        self.__lock = Lock()
        self.__player = QMediaPlayer()
        self.__player.setVolume(50)
        self.__player.positionChanged.connect(self.onPositionChanged)

    def play(self, path: str):
        self.__lock.acquire()
        """
        开始或继续播放。如果以前已暂停播放，则将从暂停的位置继续播放。
        如果播放已停止或之前从未开始过，则播放将从头开始。
        """
        status = self.__player.mediaStatus()
        if status == QMediaPlayer.NoMedia or self.__path != path:
            self.stop()
            temp = path
            if not path.endswith(".wav"):
                # TODO: 缓存
                dest = "D:/temp.wav"
                Commons.export2wave(path, dest)
                temp = dest
            content = QMediaContent(QUrl.fromLocalFile(temp))
            self.__player.setMedia(content)
        self.__path = path
        state = self.__player.state()
        if state == QMediaPlayer.PlayingState:
            self.__player.pause()
        else:
            self.__player.play()
        player_state = self.__player.state()
        self.stateChanged.emit(player_state)
        self.__lock.release()

    def pause(self):
        """ 暂停播放 """
        self.__player.pause()
        self.stateChanged.emit(self.__player.state())

    def stop(self):
        self.__player.stop()
        self.__player.setMedia(QMediaContent())

    def getVolume(self) -> int:
        """ 获取音量 """
        return self.__player.volume()

    def setVolume(self, volume: int):
        """
        设置音量, 范围从0(静音)到100(全音量).
        默认情况下，音量为100.
        """
        self.__player.setVolume(volume)
        self.volumeChanged.emit(volume)

    def getMuted(self) -> bool:
        """ 获取静音状态. """
        return self.__player.isMuted()

    def setMuted(self, muted: bool):
        """ 设置静音状态. """
        self.__player.setMuted(muted)
        self.mutedChanged.emit(muted)

    def getState(self) -> int:
        """ 获取播放状态. """
        return self.__player.state()

    def playing(self) -> bool:
        """ 当前是否处于播放状态. """
        return self.__player.state() == QMediaPlayer.PlayingState

    def setPosition(self, position: int):
        """
        跳跃到指定的时间位置。
        :param position: 绝对时间位置, 毫秒。
        """
        self.__player.setPosition(position)
        self.positionChanged.emit(position)

    def getPosition(self) -> int:
        """ 获取当前播放进度. """
        return self.__player.position()

    def getDuration(self) -> int:
        """ 获取时长. """
        return self.__player.duration()

    def onPositionChanged(self, position: int):
        self.positionChanged.emit(position)
