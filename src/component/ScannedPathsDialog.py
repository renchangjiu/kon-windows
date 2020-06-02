from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QFileDialog

from src.Apps import Apps
from src.common.Optionals import Optionals
from src.component.ScanPaths import ScanPaths
from src.component.config.ScannedPath import ScannedPath
from src.ui.ScannedPathDialogUI import Ui_Dialog


class ScannedPathsDialog(QtWidgets.QDialog, Ui_Dialog):
    """ 选择本地音乐目录 页面 """

    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self)
        Ui_Dialog.__init__(self)
        self.setParent(parent)
        self.setupUi(self)

        self.scanned_paths = Apps.config.scanned_paths.copy()
        self.init_ui()
        self.init_data()
        self.init_connect()

    def init_connect(self):
        self.btn_close.clicked.connect(self.close)
        self.btn_add.clicked.connect(self.show_dialog)
        self.btn_confirm.clicked.connect(self.on_confirm)

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

    # 判断要添加的path是否已经存在, 已存在则返回其check状态("checked" or "unchecked"), 否则返回""
    def in_paths(self, path):
        for p in self.pre_paths:
            if path == p[0]:
                return p[1]
        return ""

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
        if len(new.union(old)) != len(new) and len(new.union(old)) != len(old):
            scan = ScanPaths()
            scan.scan_state_change.connect(self.on_scan)
            scan.start()
        self.close()

    def on_scan(self, state: int):
        self.parent().on_scan(state)
        if state == 1:
            self.parent().label_search_state.setText("正在更新本地音乐列表...")
        else:
            self.parent().label_search_state.setText("更新完成")

    def init_ui(self):
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        # self.setModal(True)
        self.setWindowModality(Qt.WindowModal)
        self.setGeometry((self.parent().width() - self.width()) / 2, (self.parent().height() - self.height()) / 2, 0, 0)
        # scrollArea -> scrollAreaWidgetContents -> verticalLayout
        self.setStyleSheet("background:#fafafa;border-right:1px solid #c8c8c8;")
        self.header.setStyleSheet(
            "QWidget#header{border:1px solid #c8c8c8;border-bottom:1px solid #e1e1e2;background:#fafafa;}")
        self.label_2.setStyleSheet("border-left:1px solid #c8c8c8;border-right:1px solid #c8c8c8;")
        self.scrollArea.setStyleSheet(
            "QScrollArea#scrollArea{border:none;border-left:1px solid #c8c8c8;}")
        self.scrollAreaWidgetContents.setStyleSheet("{font-size:16px;}")
        self.label.setStyleSheet("border:none")
        self.scrollAreaWidgetContents.setStyleSheet(
            "QWidget{border:none;}"
            "QCheckBox::indicator::unchecked{image:url(./resource/image/checkbox-unchecked.png);}" +
            "QCheckBox::indicator::checked{image:url(./resource/image/checkbox-checked.png);}")

        self.scrollArea.verticalScrollBar().setStyleSheet("QScrollBar{background:#fafafa; width:8px;border:none;}"
                                                          "QScrollBar::handle{border:none;background:#e1e1e2; border-radius:4px;}"
                                                          "QScrollBar::handle:hover{background:#cfcfd1;}"
                                                          "QScrollBar::sub-line{none;}"
                                                          "QScrollBar::add-line{background:transparent;}")
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.footer.setStyleSheet(
            "QWidget#footer{border:1px solid #c8c8c8;border-top:1px solid #e1e1e2;background:#f5f5f7;}")

        self.btn_close.setStyleSheet("QPushButton{border-image:url(./resource/image/choose-music-dir-page-关闭.png)}")
        self.btn_confirm.setStyleSheet(
            "QPushButton{width:80px; height:28px;color:#ffffff;border: 1px solid #e1e1e2;background-color:#0c73c2;border-radius:5px}" +
            "QPushButton:hover{background-color:#1167a8}")
        self.btn_add.setStyleSheet(
            "QPushButton{width:80px; height:28px;border: 1px solid #e1e1e2;background-color:#ffffff;border-radius:5px}" +
            "QPushButton:hover{background-color:#f5f5f7}")
        self.btn_close.setCursor(Qt.PointingHandCursor)
        self.btn_confirm.setCursor(Qt.PointingHandCursor)
        self.btn_add.setCursor(Qt.PointingHandCursor)
        self.header.setCursor(Qt.SizeAllCursor)
