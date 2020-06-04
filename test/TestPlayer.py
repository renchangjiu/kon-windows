import sys, time
import threading
import unittest
from datetime import datetime

from src.component.Constant import Constant
from src.component.Player import Player


class MyTestCase(unittest.TestCase):
    def test_player(self):
        Constant.res = "D:/su/GitHub/kon-windows/src"
        player = Player()
        player.prepare("D:/su/music/洛天依 乐正绫 - 灼之花.mp3").start()
        threading.Thread(target=self.sub_thread).start()
        time.sleep(5)
        pass

    def sub_thread(self):
        while True:
            print(datetime.now())
        pass


if __name__ == '__main__':
    unittest.main()
