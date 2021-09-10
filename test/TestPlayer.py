import sys
import os
import time
import random
from pathlib import Path
from threading import Thread

from PyQt5 import QtWidgets

from src.component.Player import Player


def test1():
    app = QtWidgets.QApplication(sys.argv)
    player = Player()

    path = Path("C:/Users/win10/Desktop/a")
    iter_ = path.iterdir()
    for file in iter_:
        path_ = str(file)
        Thread(target=sub, args=(path_, player)).start()
        time.sleep(10)
    sys.exit(app.exec())


def sub(path, player: Player):
    # print(path)
    player.volumeChanged.connect(volumeChanged)
    player.stateChanged.connect(stateChanged)
    player.play(path)
    player.setVolume(random.randint(20, 100))


def volumeChanged(volume: int):
    print("volumeChanged: currentValue = " + str(volume))


def stateChanged(state):
    print(state)


if __name__ == '__main__':
    test1()
