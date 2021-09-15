import time

from src.component.Playlist import Playlist
from src.dao.MusicDao import MusicDao
from src.dao.MusicListDao import MusicListDao
from src.model.MusicList import MusicList


class MusicListService:
    def __init__(self) -> None:
        super().__init__()
        self.music_dao = MusicDao()
        self.music_list_dao = MusicListDao()

    def init(self):
        self.music_dao.init()
        self.music_list_dao.init()
        return self

    @staticmethod
    def copy(source: MusicList) -> MusicList:
        """ 将源歌单的所有属性复制到一个新对象"""
        ret = MusicList()
        ret.name = source.name
        ret.play_count = source.play_count
        ret.created = source.created
        ret.musics = source.musics[0:len(source.musics)]
        return ret

    def list_(self, ml: MusicList) -> tuple:
        """ 按条件查询 """
        return tuple(self.music_list_dao.list_(ml))

    def get_local_music(self) -> MusicList:
        """获取本地音乐歌单, 同时查出该歌单下的所属音乐"""
        music_list = self.music_list_dao.get(MusicList.DEFAULT_ID)
        musics = self.music_dao.list_by_mid(music_list.id)
        music_list.musics = musics
        return music_list

    def get(self, id_: int) -> MusicList:
        """ 根据ID获取歌单信息, 同时获取该歌单的所属音乐 """
        music_list = self.music_list_dao.get(id_)
        musics = self.music_dao.list_by_mid(id_)
        music_list.musics = musics
        return music_list

    def logic_delete(self, _id: int):
        """逻辑删除该歌单"""
        self.music_list_dao.logic_delete(_id)

    def play_count_incr(self, _id: int):
        """ 使该歌单的播放数+1 """
        self.music_list_dao.play_count_incr(_id)

    def insert(self, name: str):
        """新增歌单, 只需要name属性"""
        ml = MusicList()
        ml.name = name
        ml.created = int(time.time())
        self.music_list_dao.insert(ml)

    @staticmethod
    def to_playlist(music_list: MusicList) -> Playlist:
        """ 把MusicList 转成 Playlist """
        playlist = Playlist()
        playlist.setMusics(music_list.musics)
        return playlist


if __name__ == "__main__":
    pass
