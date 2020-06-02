import os
import threading

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QFileDialog

from src.Apps import Apps
from src.component.config.ScannedPath import ScannedPath
from src.component.ScanPaths import ScanPaths
from src.ui.ScannedPathDialogUI import Ui_Dialog


class ChooseMusicDirPage(QtWidgets.QDialog, Ui_Dialog):
    local_musics_change = QtCore.pyqtSignal()

    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self)
        Ui_Dialog.__init__(self)
        self.setParent(parent)
        self.setupUi(self)
        self.config = Apps.config
        # 记录下修改path之前的path, 以便在修改之后判断是否需要重新搜索音乐
        self.pre_paths = []
        self.init_ui()
        self.init_data()
        self.init_connect()

    def init_connect(self):
        self.btn_close.clicked.connect(self.close)
        self.btn_add.clicked.connect(self.show_dialog)
        self.btn_confirm.clicked.connect(self.on_confirm)

    def add_checkbox(self, text: str, checked: bool):
        # 特殊字符, 把一个 &, 替换成两个 &&, 以正常显示一个&
        # error, 上述方法会导致bug
        # check_box = QCheckBox(text.replace("&", "&&"), self.scrollAreaWidgetContents)
        check_box = QCheckBox(text, self.scrollAreaWidgetContents)
        check_box.setToolTip(text)
        check_box.setCheckState(Qt.Checked if checked else Qt.Unchecked)
        self.verticalLayout.addWidget(check_box, alignment=Qt.AlignTop)
        return check_box

    def init_data(self):
        count = self.verticalLayout.count()
        for i in range(count):
            self.verticalLayout.itemAt(i).widget().deleteLater()
        scanned_paths = self.config.scanned_paths
        for scp in scanned_paths:
            self.add_checkbox(scp.path, scp.checked)

    def show_dialog(self):
        path = QFileDialog.getExistingDirectory(self, "选择添加目录", r"C:/", QFileDialog.ShowDirsOnly)
        if path.strip() != "":
            path = path.replace("\\", "/")
            ScannedPath.add(ScannedPath(path, True), self.config.scanned_paths)
            self.init_data()

    # 判断要添加的path是否已经存在, 已存在则返回其check状态("checked" or "unchecked"), 否则返回""
    def in_paths(self, path):
        for p in self.pre_paths:
            if path == p[0]:
                return p[1]
        return ""

    def on_confirm(self):
        ret = []
        count = self.verticalLayout.layout().count()
        for i in range(count):
            at = self.verticalLayout.layout().itemAt(i)
            if at != 0:
                checkbox = at.widget()
                temp = [checkbox.text()]
                if checkbox.checkState() == Qt.Checked:
                    temp.append("checked")
                elif checkbox.checkState() == Qt.Unchecked:
                    temp.append("unchecked")
                ret.append(temp)
        self.config.save()
        self.compare_two_path(ret)
        # 重新为previous path 赋值
        self.pre_paths.clear()
        for path in ret:
            self.pre_paths.append(path)
        self.close()

    # 比较path修改前后的变化(多一个 or 少一个)
    def compare_two_path(self, cur_paths):
        change_paths = []
        # 因为已添加的目录不可被删除, 所以previous-paths总是current-paths的子集
        for path in cur_paths:
            pre_state = self.in_paths(path[0])
            # 如果该path 已存在,
            if pre_state != "":
                # 如果state不同, 则返回当前state
                if path[1] != pre_state:
                    change_paths.append(path)
            # 不存在, 根据其是否被check, 判断
            else:
                if path[1] == "checked":
                    change_paths.append(path)
        # 如果path有变化, 则重新搜索新的path
        if len(change_paths) != 0:
            # print(cur_paths)
            search_local_music = ScanPaths()
            search_local_music.begin_search.connect(self.begin)
            search_local_music.end_search.connect(self.end)
            thread = threading.Thread(target=lambda: self.sub_thread(search_local_music, cur_paths))
            thread.start()

    def begin(self):
        self.parent().begin_search()
        self.parent().label_search_state.setText("正在更新本地音乐列表...")

    def end(self):
        self.parent().end_search()
        self.parent().label_search_state.setText("更新完成")
        # 发出信号, 通知父窗口更新本地音乐
        self.local_musics_change.emit()

    def sub_thread(self, search_local_music, change_paths):
        paths = []
        for path in change_paths:
            if path[1] == "checked" and os.path.exists(path[0]):
                paths.append(path[0])
        print(paths)
        search_local_music.search_in_path(paths)

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
