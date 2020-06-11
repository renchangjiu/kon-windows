from src.model.Music import Music
from src.util.Jsons import Jsons


class MusicList:
    """歌单"""

    # 默认歌单(即本地歌单)ID
    DEFAULT_ID = 0

    def __init__(self):
        # 歌单id
        self.id = None

        # 歌单名
        self.name = None

        # 创建日期(秒级时间戳)
        self.created = None
        self.created_label = ""

        # 播放次数
        self.play_count = None

        # 所属歌单音乐列表
        self.musics = []

    def get(self, index) -> Music:
        return self.musics[index]

    def __str__(self):
        obj = {
            "id": self.id,
            "name": self.name,
        }
        return Jsons.dumps(obj)


if __name__ == "__main__":
    pass
