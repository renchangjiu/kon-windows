import os
import threading

from PyQt5 import QtCore
from PyQt5.QtCore import QObject

from src.Apps import Apps
from src.model.Music import Music
from src.model.MusicList import MusicList
from src.service.MP3Parser import MP3


class ScanPaths(QObject, threading.Thread):
    """ 异步扫描指定目录(指配置文件)下的所有音乐文件, 并写入数据库 """

    # 1/2, 1: 扫描开始, 2: 扫描结束
    scan_state_change = QtCore.pyqtSignal(int)

    def __init__(self):
        super().__init__()

    @staticmethod
    def scan(slot_func):
        scan = ScanPaths()
        scan.scan_state_change.connect(slot_func)
        scan.start()

    def run(self) -> None:
        self.scan_state_change.emit(1)
        search_paths = list(map(lambda v: v.path, filter(lambda v: v.checked, Apps.config.scanned_paths)))
        music_files = ScanPaths.__find_music_files(search_paths)
        musics = ScanPaths.__get_mp3_info(music_files)
        Apps.music_service.batch_insert(musics)
        self.scan_state_change.emit(2)

    @staticmethod
    def __find_music_files(search_paths: list) -> list:
        files = list()
        while len(search_paths) > 0:
            size = len(search_paths)
            for i in range(size):
                pop = search_paths.pop()
                if not os.path.exists(pop):
                    continue
                listdir = list(map(lambda v: os.path.join(pop, v), ScanPaths.__listdir(pop)))
                for ld in listdir:
                    if os.path.isdir(ld):
                        search_paths.append(ld)
                    else:
                        if ScanPaths.__is_music_file(ld):
                            files.append(ld)
        return files

    @staticmethod
    def __is_music_file(path):
        if (path.endswith("mp3") or path.endswith("MP3")) and os.path.getsize(path) > 100 * 1024:
            return True
        return False

    @staticmethod
    def __get_mp3_info(paths: list):
        musics = []
        for path in paths:
            try:
                mp3 = MP3(path)
                if mp3.ret["has-ID3V2"] and mp3.duration >= 30:
                    size = os.path.getsize(path)
                    if size < 1024 * 1024:
                        size = str(int(size / 1024)) + "KB"
                    else:
                        size = str(round(size / 1024 / 1024, 1)) + "MB"

                    title = mp3.title
                    if title == "":
                        title = os.path.basename(path)

                    artist = mp3.artist
                    if artist == "":
                        artist = "未知歌手"

                    album = mp3.album
                    if album == "":
                        album = "未知专辑"

                    duration = mp3.duration
                    music = Music()
                    music.mid = MusicList.DEFAULT_ID
                    music.path = path
                    music.title = title
                    music.artist = artist
                    music.album = album
                    music.duration = duration
                    music.size = size
                    musics.append(music)
            except IndexError as e:
                pass
            except UnicodeDecodeError as e1:
                pass
        return musics

    @staticmethod
    def __listdir(path):
        try:
            return os.listdir(path)
        except PermissionError as e:
            print(e.strerror)
            return []
