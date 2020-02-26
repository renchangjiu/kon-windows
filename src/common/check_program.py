import os
import shutil

from src.common.app_attribute import AppAttribute
from src.entity.music_list import MusicList
from src.service.music_service import MusicService


class CheckProgram:

    @staticmethod
    def check_program():
        """检查程序完整性"""
        db_file = AppAttribute.data_path + "/data.db"
        if not os.path.exists(db_file):
            shutil.copyfile(AppAttribute.data_path + "/empty.db", db_file)
            music_service = MusicService()
            path = AppAttribute.res_path + "/放課後ティータイム - Listen!!.mp3"
            music = music_service.gen_music_by_path(path, MusicList.DEFAULT_ID)
            music_service.insert(music)
