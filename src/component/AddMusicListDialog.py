from PyQt5 import QtCore, QtWidgets

from src.ui.AddMusicListDialogUI import Ui_Dialog


class AddMusicListDialog(QtWidgets.QDialog, Ui_Dialog):
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

        self.setStyleSheet("QDialog{border:2px solid #c8c8c9; border-radius:5px}")
        self.label.setStyleSheet("color:333333;font-size:20px")
        self.lineEdit.setStyleSheet("border:2px solid #e1e1e2")
        self.lineEdit.setPlaceholderText("请输入歌单标题")

        self.cancel.setStyleSheet(
            "QPushButton{width:80px; height:28px;border: 1px solid #e1e1e2;background-color:#ffffff;border-radius:5px}" +
            "QPushButton:hover{background-color:#f5f5f7}")
        self.confirm.setStyleSheet(
            "QPushButton{width:80px; height:28px;color:#b5d3ea;border: 1px solid #e1e1e2;background-color:#96c0e1;border-radius:5px}")
        self.cancel.setCursor(QtCore.Qt.PointingHandCursor)
        self.confirm.setEnabled(False)

    def init_connect(self):
        self.lineEdit.textChanged.connect(self.on_text_changed)
        self.cancel.clicked.connect(self.hide)

    def positive(self, callback):
        self.confirm.clicked.connect(lambda: self.positive_func(callback))
        return self

    def positive_func(self, callback):
        self.hide()
        callback(self.lineEdit.text())

    def on_text_changed(self):
        text = self.lineEdit.text()
        if len(text.strip()) != 0:
            self.confirm.setEnabled(True)
            self.confirm.setStyleSheet(
                "QPushButton{width:80px; height:28px;color:#ffffff;border: 1px solid #e1e1e2;background-color:#0c73c2;border-radius:5px}" +
                "QPushButton:hover{background-color:#1167a8}")
        else:
            self.confirm.setEnabled(False)
            self.confirm.setStyleSheet(
                "QPushButton{width:80px; height:28px;color:#b5d3ea;border: 1px solid #e1e1e2;background-color:#96c0e1;border-radius:5px}")
