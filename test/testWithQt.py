import sys

from PyQt5 import QtWidgets


def test():
    app = QtWidgets.QApplication(sys.argv)

    sys.exit(app.exec())


if __name__ == '__main__':
    test()
