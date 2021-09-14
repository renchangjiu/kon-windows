import os
from threading import Lock

from PyQt5 import QtCore
from PyQt5.QtCore import QObject, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer

from src.model.Music import Music
from src.util.Commons import Commons


class Player(QObject):
    # 信号: 当音量变化时, 参数为当前音量.
    volumeChanged = QtCore.pyqtSignal(int)

    # 信号: 当播放位置变化时, 参数为当前位置
    positionChanged = QtCore.pyqtSignal(int)

    # 信号: 当播放状态变化时, 参数为当前状态
    stateChanged = QtCore.pyqtSignal(int)

    # 信号: 当媒体状态变化时, 参数为当前状态
    mediaStatusChanged = QtCore.pyqtSignal(int)

    # 信号: 当静音状态变化时, 参数为当前状态
    mutedChanged = QtCore.pyqtSignal(int)
    localAppDataDir = os.getenv("LOCALAPPDATA")
    # like:
    #   Windows: C:/Users/win10/AppData/Local/kon-windows/Temp/Music
    #   Linux  : Not test.
    tempDir = localAppDataDir + "/kon-windows/Temp/Music/"

    def __init__(self) -> None:
        super().__init__()
        self.__path = None
        self.__lock = Lock()
        self.__player = QMediaPlayer()
        self.__player.setVolume(50)
        self.__player.positionChanged.connect(self.__onPositionChanged)
        self.__player.mediaStatusChanged.connect(self.__onMediaStatusChanged)
        if not os.path.exists(self.tempDir):
            os.makedirs(self.tempDir)

    def init(self):
        pass

    def play(self, music: Music):
        self.__lock.acquire()
        """
        开始或继续播放。如果以前已暂停播放，则将从暂停的位置继续播放。
        如果播放已停止或之前从未开始过，则播放将从头开始。
        """
        status = self.__player.mediaStatus()
        path = music.path
        if status == QMediaPlayer.NoMedia or self.__path != path:
            self.stop()
            content = QMediaContent(QUrl.fromLocalFile(self.__trans2wave(music)))
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

    def toggleMuted(self):
        """ 切换静音状态. """
        self.__player.setMuted(not self.__player.isMuted())
        self.mutedChanged.emit(self.__player.isMuted())

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

    def __onPositionChanged(self, position: int):
        self.positionChanged.emit(position)

    def __onMediaStatusChanged(self, mediaStatus: int):
        self.mediaStatusChanged.emit(mediaStatus)

    def __trans2wave(self, music: Music) -> str:
        """ 转换格式为 wave """
        path = music.path
        if path.endswith(".wav"):
            return path
        dest = self.tempDir + str(music.id) + ".wav"
        if os.path.exists(dest):
            return dest
        # 最多保留一百个歌曲缓存
        olds = os.listdir(self.tempDir)
        if len(olds) >= 100:
            # 删掉一个
            os.remove(self.tempDir + olds[0])
        Commons.export2wave(path, dest)
        return dest
