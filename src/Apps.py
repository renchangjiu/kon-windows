import os
import shutil

from src.component.Const import Const
from src.component.Playlist import Playlist
from src.component.config.Config import Config
from src.model.MusicList import MusicList
from src.service.MusicListService import MusicListService
from src.service.MusicService import MusicService


class Apps(object):
    """ 维护应用运行时的复杂对象 """
    config = Config()
    music_service = MusicService()
    music_list_service = MusicListService()
    playlist = Playlist()

    @classmethod
    def init(cls):
        cls.config.init()
        cls.music_service.init()
        cls.music_list_service.init()
        cls.playlist.init()

    @staticmethod
    def check_app():
        """ 检查程序完整性 """
        if not os.path.exists(Const.data):
            os.mkdir(Const.data)
        db_file = Const.data + "/data.db"
        if not os.path.exists(db_file):
            shutil.copyfile(Const.res + "/example.data.db", db_file)
            music_service = MusicService()
            music_service.init()
            path = Const.res + "/放課後ティータイム - Listen!!.mp3"
            music = music_service.gen_music_by_path(path, MusicList.DEFAULT_ID)
            music_service.insert(music)

        config_path = Const.data + "/config.json"
        if not os.path.exists(config_path):
            shutil.copyfile(Const.res + "/example.config.json", config_path)
