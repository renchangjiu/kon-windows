import sys
import time
from threading import Thread

from PyQt5 import QtMultimedia
from PyQt5 import QtWidgets
from PyQt5.QtCore import QUrl

from src.util.Commons import Commons


def test():
    app = QtWidgets.QApplication(sys.argv)
    src = "C:/Users/win10/Desktop/a/01. ふゆびより.flac"
    dest = "C:/Users/win10/Desktop/temp.wav"
    Commons.export2wave(src, dest)
    file = QUrl.fromLocalFile(dest)  # 音频文件路径
    content = QtMultimedia.QMediaContent(file)
    player = QtMultimedia.QMediaPlayer()
    player.setMedia(content)
    player.setVolume(30)
    player.play()
    playlist = player.playlist()
    media = playlist.currentMedia()
    print(media)


    sys.exit(app.exec())






if __name__ == "__main__":
    test()
