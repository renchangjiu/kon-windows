import sys

from PyQt5 import QtWidgets

from src.Apps import Apps
from src.component.Const import Const
from src.component.MainWindow import MainWindow


# TODO 滚动歌词: verticalScrollBar.setValue()
# TODO 如果要播放的文件不存在:  0. 右键播放, 1. 正在的播放的文件被删除, 4. 双击歌单列表, 但目标文件已被删除, 5. 双击播放列表, ..., 6. 要删除已被删除的文件
# TODO table widget 列宽可调节
# TODO UI细节调整
# todo 歌单图片
# TODO 重构 & 拆分入口文件
def main():
    Const.init(sys.argv)
    Apps.check_app()
    Apps.init()

    app = QtWidgets.QApplication(sys.argv)
    my_window = MainWindow()
    my_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
