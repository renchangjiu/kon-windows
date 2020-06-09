from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QCursor

from src.common.QssHelper import QssHelper
from src.ui.AddMusicListDialogUI import Ui_Dialog


class AddMusicListDialog(QtWidgets.QDialog, Ui_Dialog):
    """ 创建歌单页面。 """

    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        Ui_Dialog.__init__(self)
        self.setupUi(self)
        self.init_ui()
        self.init_connect()

    def init_ui(self):
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setModal(True)
        self.lineEdit.setFocus()
        self.setStyleSheet(QssHelper.load("/AddMusicListDialogUI.css"))
        self.cancel.setCursor(QtCore.Qt.PointingHandCursor)
        self.confirm.setEnabled(False)

    def init_connect(self):
        self.lineEdit.textChanged.connect(lambda: self.confirm.setEnabled(len(self.lineEdit.text().strip()) != 0))
        self.cancel.clicked.connect(self.hide)

    @staticmethod
    def show_(parent, positive_callback):
        dialog = AddMusicListDialog()
        dialog.setParent(parent)
        pos = dialog.mapFromGlobal(QCursor.pos())
        dialog.setGeometry(pos.x() + 20, pos.y() - 30, 270, 210)
        dialog.positive(positive_callback)
        dialog.show()

    def positive(self, callback):
        self.confirm.clicked.connect(lambda: self.__positive_func(callback))
        return self

    def __positive_func(self, callback):
        self.hide()
        callback(self.lineEdit.text())
