import os
import shutil

from src.component.Const import Const
from src.component.Player import Player
from src.component.Playlist import Playlist
from src.component.config.Config import Config
from src.model.MusicList import MusicList
from src.service.MusicListService import MusicListService
from src.service.MusicService import MusicService


class Apps(object):
    """ 统一管理全局对象 """
    config = Config()
    musicService = MusicService()
    musicListService = MusicListService()
    playlist = Playlist()
    player = Player()

    @classmethod
    def init(cls):
        cls.config.init()
        cls.musicService.init()
        cls.musicListService.init()
        cls.playlist.init()
        cls.player.init()

    @staticmethod
    def check_app():
        """ 检查程序完整性 """
        if not os.path.exists(Const.data):
            os.mkdir(Const.data)
        db_file = Const.data + "/data.db"
        if not os.path.exists(db_file):
            shutil.copyfile(Const.res + "/example.data.db", db_file)
            musicService = MusicService()
            musicService.init()
            path = Const.res + "/放課後ティータイム - Listen!!.mp3"
            music = musicService.gen_music_by_path(path, MusicList.DEFAULT_ID)
            musicService.insert(music)

        config_path = Const.data + "/config.json"
        if not os.path.exists(config_path):
            shutil.copyfile(Const.res + "/example.config.json", config_path)
