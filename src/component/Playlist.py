import json
import os

from PyQt5 import QtCore
from PyQt5.QtCore import QObject

from src.service.MusicService import MusicService
from src.util.IOs import IOs
from src.component.Const import Const
from src.model.Music import Music


class Playlist(QObject):
    """
    播放列表
        根据path & from 来判断是否是来自同一歌单同一首音乐
    """

    # Music is current-music
    current_music_change = QtCore.pyqtSignal(Music)

    # 播放模式: 列表循环
    MODE_LOOP = 1

    # 播放模式: 随机播放
    MODE_RANDOM = 2

    # 播放模式: 单曲循环
    MODE_SINGLE_LOOP = 3

    def __init__(self):
        super().__init__()
        self.__musics = []
        self.mode = 1
        self.index = -1
        self.position = -1
        self.volume = 50
        self.mute = 0

    def get_musics(self):
        return self.__musics

    def set_musics(self, musics):
        self.__musics = musics

    def set_mode(self, mode: int):
        self.mode = mode

    def get_mode(self):
        return self.mode

    def add_music(self, music):
        self.__musics.append(music)

    def insert(self, index, music):
        self.__musics.insert(index, music)

    def size(self):
        return len(self.__musics)

    def isEmpty(self):
        return len(self.__musics) == 0

    def getIndex(self):
        return self.index

    def get(self, index):
        return self.__musics[index]

    def remove(self, music):
        index = self.index_of(music)
        # print("index ", index)
        if index != -1:
            self.__musics.pop(index)
            if index <= self.index:
                if self.index != 0:
                    self.index -= 1
                if self.size() == 0:
                    self.index = -1

    def removeBatch(self, musics: list):
        for m in musics:
            self.remove(m)

    # 根据索引删除
    def __remove_2(self, index):
        print(index)
        self.__musics.pop(index)
        if index < self.index:
            print("<")
            self.index -= 1

    def clear(self):
        self.__musics = list()
        self.index = -1

    def contains(self, path):
        for music in self.__musics:
            if music.path == path:
                return True
        return False

    def index_of(self, music):
        for i in range(self.size()):
            m = self.get(i)
            if self.is_same_music(m, music):
                return i
        return -1

    # 来自于同歌单且path相同的music将被判断为 相同的music
    def is_same_music(self, one: Music, another: Music):
        if type(one) == type(another):
            if one.path == another.path and one.mid == another.mid:
                return True
        return False

    def setIndex(self, index):
        """ 设置当前播放的歌曲下标 """
        if self.size() > 0:
            self.index = index
            self.current_music_change.emit(self.getCurrentMusic())

    def getCurrentMusic(self) -> Music:
        if self.size() > 0:
            return self.__musics[self.index]

    def get_music(self, index):
        return self.__musics[index]

    def next(self) -> Music:
        if self.mode == self.MODE_LOOP:
            # 如果索引是play_list 的最后一项, 则置索引为0
            if self.index == self.size() - 1:
                self.index = 0
            else:
                self.index += 1
            self.current_music_change.emit(self.getCurrentMusic())
        return self.getCurrentMusic()

    def previous(self):
        if self.mode == self.MODE_LOOP:
            # 如果索引是play_list 的第一项, 则置索引为length-1(即最后一项)
            if self.index == 0:
                self.index = self.size() - 1
            else:
                self.index -= 1
            self.current_music_change.emit(self.getCurrentMusic())

    def init(self):
        if not os.path.exists(Const.dp("/playlist.json")):
            self.save()
        obj = json.loads(IOs.read(Const.dp("/playlist.json")))
        ids = obj["ids"]
        list_ = MusicService().init().batch_get(ids)
        print(obj)

    def save(self):
        obj = self.__structure()
        IOs.write(Const.dp("/playlist.json"), json.dumps(obj))

    def __structure(self) -> dict:
        return {
            "ids": list(map(lambda v: v.id, self.__musics)),
            "mode": self.mode,
            "index": self.index,
            "position": self.position,
            "volume": self.volume,
            "mute": self.mute
        }

    def __str__(self):
        if len(self.__musics) != 0:
            ret = "PlayerList %d [" % self.size()
            for i in range(len(self.__musics)):
                ret += "\t"
                ret += self.__musics[i].path
                ret += ",\t\t"
                ret += self.__musics[i].title
                ret += "\n"
            ret += "]"
            return ret
        else:
            return "PlayerList[Empty]"
