import os
import shutil

from src.component.Constant import Constant
from src.component.config.Config import Config
from src.model.MusicList import MusicList
from src.service.MusicService import MusicService


class Apps(object):
    """ 维护应用运行时的复杂对象 """
    config = Config()

    @classmethod
    def init(cls):
        cls.config.init()

    @staticmethod
    def check_app():
        """ 检查程序完整性 """
        if not os.path.exists(Constant.data):
            os.mkdir(Constant.data)
        db_file = Constant.data + "/data.db"
        if not os.path.exists(db_file):
            shutil.copyfile(Constant.res + "/example.data.db", db_file)
            music_service = MusicService()
            path = Constant.res + "/放課後ティータイム - Listen!!.mp3"
            music = music_service.gen_music_by_path(path, MusicList.DEFAULT_ID)
            music_service.insert(music)

        config_path = Constant.data + "/config.json"
        if not os.path.exists(config_path):
            shutil.copyfile(Constant.res + "/example.config.json", config_path)
