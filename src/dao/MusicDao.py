import sqlite3

from src.component.Const import Const
from src.model.Music import Music
from src.util.Strings import Strings


class MusicDao:
    def __init__(self):
        self.database = Const.dp("/data.db")
        self.conn = sqlite3.connect(self.database, check_same_thread=False)

    def list_by_mid(self, mid: int) -> list:
        """
        根据歌单ID, 查询该歌单所属的所有歌曲
        :param mid:
        :return:
        """
        sql = "select * from t_music where mid = ?"
        musics_ = []
        cursor = self.conn.cursor()
        cursor.execute(sql, (mid,))
        res = cursor.fetchall()
        cursor.close()
        for row in res:
            m = self.__row2music(row)
            musics_.append(m)
        return musics_

    def select_by_id(self, _id: int) -> Music:
        sql = "select * from t_music where id = ?"
        cursor = self.conn.cursor()
        cursor.execute(sql, (_id,))
        res = cursor.fetchall()[0]
        cursor.close()
        music = self.__row2music(res)
        return music

    def batch_get(self, ids: list) -> list:
        sql = "select * from t_music where id in (%s)" % ",".join(ids)
        cursor = self.conn.cursor()
        cursor.execute(sql)
        res = cursor.fetchall()
        cursor.close()
        return list(map(lambda v: self.__row2music(v), res))

    def list_(self, m: Music) -> list:
        sql = "select * from t_music where 1 = 1"
        if m is not None:
            if Strings.is_not_empty(m.id):
                sql = sql + " and id = '" + str(m.id) + "'"
            if Strings.is_not_empty(m.mid):
                sql = sql + " and mid = '" + str(m.mid) + "'"
            if Strings.is_not_empty(m.path):
                sql = sql + " and path = '" + m.path + "'"
        cursor = self.conn.cursor()
        cursor.execute(sql)
        res = cursor.fetchall()
        cursor.close()
        return list(map(lambda v: self.__row2music(v), res))

    def insert(self, music: Music):
        sql = "insert into t_music values (null, ?, ?, ?, ?, ?, ?, ?)"
        self.conn.execute(sql, self.__music2row(music))
        self.conn.commit()

    def batch_insert(self, musics: list):
        """ 批量插入 """
        sql = "insert into t_music values (null, ?, ?, ?, ?, ?, ?, ?)"
        for m in musics:
            self.conn.execute(sql, self.__music2row(m))
        self.conn.commit()

    def delete(self, id_: int):
        """
        删除该歌曲
        :param id_: 歌曲ID
        """
        sql = "delete from t_music where id = ?"
        self.conn.execute(sql, (id_,))
        self.conn.commit()

    def batch_delete(self, ids_: list):
        """ 批量删除 """
        sql = "delete from t_music where id = ?"
        for _id in ids_:
            self.conn.execute(sql, (_id,))
        self.conn.commit()

    def delete_by_mid(self, mid: int):
        """ 根据歌单ID删除属于该歌单的所有歌曲 """
        sql = "delete from t_music where mid = ?"
        self.conn.execute(sql, (mid,))
        self.conn.commit()

    @staticmethod
    def __music2row(m: Music) -> tuple:
        return m.mid, m.path, m.size, m.title, m.artist, m.album, m.duration

    @staticmethod
    def __row2music(row: tuple):
        """
        把表中查询到的一行数据封装成一个Music对象
        :param row: 一行数据
        :return: Music
        """
        m = Music()
        m.id = row[0]
        m.mid = row[1]
        m.path = row[2]
        m.size = row[3]
        m.title = row[4]
        m.artist = row[5]
        m.album = row[6]
        m.duration = row[7]
        return m


if __name__ == "__main__":
    pass
