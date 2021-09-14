from src.util.Jsons import Jsons


class Music:
    def __init__(self):
        # 歌曲ID
        self.id = None

        # 所属歌单ID
        self.mid = None

        # 文件相关属性
        self.path = None
        self.size = None

        # mp3相关属性
        self.image = b""
        self.title = None
        self.artist = None
        self.album = None
        self.duration = None

    def __str__(self):
        obj = {
            "id": self.id,
            "mid": self.mid,
            "path": self.path,
            "title": self.title,
            "artist": self.artist,
            "album": self.album,
            "duration": self.duration,
            "size": self.size,
        }
        return Jsons.dumps(obj)


