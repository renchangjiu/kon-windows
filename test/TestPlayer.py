import time

from src.component.Constant import Constant
from src.component.Player import Player
from test import Test


class TestPlayer(object):
    def test_player(self):
        player = Player()
        player.prepare(Constant.res + "/放課後ティータイム - Listen!!.mp3").start()
        player.position()
        time.sleep(5)
        player.stop()


if __name__ == '__main__':
    Test.init()
    TestPlayer().test_player()
