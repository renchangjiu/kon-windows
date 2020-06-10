from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QFileDialog

from src.Apps import Apps
from src.util.Optionals import Optionals
from src.common.QssHelper import QssHelper
from src.component.ScanPaths import ScanPaths
from src.component.config.ScannedPath import ScannedPath
from src.ui.ScannedPathDialogUI import Ui_Dialog


class ScannedPathsDialog(QtWidgets.QDialog, Ui_Dialog):
    """ 选择本地音乐目录 页面 """

    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        Ui_Dialog.__init__(self)
        self.setupUi(self)

        self.scanned_paths = Apps.config.scanned_paths.copy()
        self.init_ui()
        self.init_data()
        self.init_connect()

    def init_ui(self):
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setStyleSheet(QssHelper.load("/ScannedPathsDialog.css"))

    def init_connect(self):
        self.btn_close.clicked.connect(self.close)
        self.btn_add.clicked.connect(self.show_dialog)
        self.btn_confirm.clicked.connect(self.on_confirm)

    @staticmethod
    def show_(parent):
        dialog = ScannedPathsDialog()
        dialog.setParent(parent)
        dialog.setGeometry((parent.width() - dialog.width()) / 2, (parent.height() - dialog.height()) / 2, 0, 0)
        dialog.show()

    def add_checkbox(self, scp: ScannedPath):
        # FIXME: text 不显示 & 符号
        check_box = QCheckBox(scp.path, self.scrollAreaWidgetContents)
        check_box.setToolTip(scp.path)
        check_box.setCheckState(Qt.Checked if scp.checked else Qt.Unchecked)
        self.verticalLayout.addWidget(check_box, alignment=Qt.AlignTop)

    def init_data(self):
        count = self.verticalLayout.count()
        for i in range(count):
            self.verticalLayout.itemAt(i).widget().deleteLater()
        for scp in self.scanned_paths:
            self.add_checkbox(scp)

    def show_dialog(self):
        path = QFileDialog.getExistingDirectory(self, "选择添加目录", r"C:/", QFileDialog.ShowDirsOnly)
        if path.strip() != "":
            path = path.replace("\\", "/")
            ScannedPath.add(ScannedPath(path, True), self.scanned_paths)
            self.init_data()

    def on_confirm(self):
        count = self.verticalLayout.count()
        self.scanned_paths = []
        for i in range(count):
            checkbox = self.verticalLayout.itemAt(i).widget()
            scp = ScannedPath(checkbox.text(), Optionals.trinocular(checkbox.checkState() == Qt.Checked, True, False))
            self.scanned_paths.append(scp)

        new = set(map(lambda v: v.path, filter(lambda v: v.checked, self.scanned_paths)))
        old = set(map(lambda v: v.path, filter(lambda v: v.checked, Apps.config.scanned_paths)))
        Apps.config.scanned_paths = self.scanned_paths
        Apps.config.save()

        # 判断是否需要重新扫描
        if len(new.union(old)) != len(new) or len(new.union(old)) != len(old):
            ScanPaths.scan(self.on_scan)
        self.close()

    def on_scan(self, state: int):
        self.parent().on_scan(state)
        if state == 1:
            self.parent().label_search_state.setText("正在更新本地音乐列表...")
        else:
            self.parent().label_search_state.setText("更新完成")
