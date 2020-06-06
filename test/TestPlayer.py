import time

from src.component.Constant import Constant
from src.component.Player import Player
from test import Test


class TestPlayer(object):
    def test_player(self):
        self.flag = True
        player = Player()
        player.prepare(Constant.res + "/放課後ティータイム - Listen!!.mp3").start()
        # threading.Thread(target=self.sub_thread).start()
        time.sleep(5)
        player.position()
        # player.load("C:/Users/su/Music/洛天依 - 棠梨煎雪.mp3")
        # player.prepare("C:/Users/su/Music/洛天依 - 棠梨煎雪.mp3").start()
        time.sleep(10)
        # self.flag = False
        player.stop()

    def sub_thread(self):
        while self.flag:
            pass
            # print(datetime.now())
        pass


if __name__ == '__main__':
    Test.init()
    TestPlayer().test_player()
