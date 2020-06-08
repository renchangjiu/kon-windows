from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QEvent, QModelIndex
from PyQt5.QtGui import QPixmap, QColor, QIcon, QCursor, QPainter, QPen
from PyQt5.QtWidgets import QWidget, QTableWidgetItem, \
    QAction, QMenu, QLabel, QWidgetAction, QHBoxLayout

from src.Apps import Apps
from src.model.MusicList import MusicList
from src.ui.PlaylistDialogUI import Ui_Form
from src.util import util


class PlayListDialog(QWidget, Ui_Form):
    def __init__(self, parent, ):
        QWidget.__init__(self)
        Ui_Form.__init__(self)
        self.setupUi(self)
        self.setParent(parent)
        self.music_list_service = Apps.music_list_service
        self.__init_ui()
        self.__init_table_widget_ui()
        self.__set_table_widget_width()
        self.init_connect()

    def init_connect(self):
        self.tableWidget.cellPressed.connect(self.open_music_list)
        self.tableWidget.customContextMenuRequested.connect(self.on_right_click)
        self.tableWidget.doubleClicked.connect(self.on_tb_double_clicked)

    # 当存放音乐列表的表格被双击
    def on_tb_double_clicked(self, index: QModelIndex):
        index = index.row()
        self.parent().cur_play_list.set_current_index(index)
        self.parent().label_play_count.setText(str(self.parent().cur_play_list.size()))
        self.parent().stop_current()
        self.parent().play()
        self.tableWidget.selectRow(index)

        if self.parent().is_mute:
            self.parent().process.write(b"mute 1\n")
        self.parent().btn_start.setStyleSheet("QPushButton{border-image:url(./resource/image/暂停.png)}" +
                                              "QPushButton:hover{border-image:url(./resource/image/暂停2.png)}")
        # 读取音乐名片
        self.parent().show_music_info()
        self.parent().state = self.parent().playing_state

    def open_music_list(self, row, column):
        # 若点击的是链接按钮, 则跳转到对应的歌单页面
        if column == 3:
            music = self.parent().cur_play_list.get(row)
            music_list = self.music_list_service.get_by_id(music.mid)
            self.parent().navigation.setFocus()
            self.parent().navigation.setCurrentRow(2)

            items = self.parent().navigation.findItems(music_list.name, Qt.MatchCaseSensitive)
            item = None
            for item_ in items:
                data = item_.data(Qt.UserRole)
                if music.mid == data.id:
                    item = item_
                    break

            if item is not None:
                data = item.data(Qt.UserRole)
                self.parent().navigation.setCurrentItem(item)
                self.parent().update_music_list(data.id)
                # 若是本地音乐
                if data.id == 0:
                    self.parent().stackedWidget_2.setCurrentWidget(self.parent().local_music_page)
                # 若是其他歌单
                else:
                    self.parent().stackedWidget_2.setCurrentWidget(self.parent().music_list_detail)
                    self.parent().show_musics_data()
            self.hide()

    def on_right_click(self):
        self.play_list_menu.clear()
        act1 = self.create_widget_action("./resource/image/nav-播放.png", "播放(Enter)")
        act2 = QAction("收藏到歌单(Ctrl+S)", self)
        act3 = self.create_widget_action("./resource/image/打开文件.png", "打开文件所在目录")
        act4 = self.create_widget_action("./resource/image/删除.png", "从列表中删除(Delete)")
        self.play_list_menu.addAction(act1)
        self.play_list_menu.addAction(act2)

        # 获取被选中的行, 包括列
        items = self.tableWidget.selectedItems()
        # 被选中的行号
        rows = set()
        for item in items:
            rows.add(item.row())
        musics = []
        for row in rows:
            music = self.parent().cur_play_list.get(row)
            musics.append(music)
        # 只选中了一行
        if len(rows) == 1:
            self.play_list_menu.addAction(act3)
        # 设置子菜单归属于act2
        self.create_collect_menu(musics)
        act2.setMenu(self.collect_menu)
        self.play_list_menu.addMenu(self.collect_menu)

        self.play_list_menu.addSeparator()
        self.play_list_menu.addAction(act4)
        act1.triggered.connect(lambda: self.parent().on_act_play(musics))
        act3.triggered.connect(lambda: self.parent().on_act_open_file(musics))
        act4.triggered.connect(lambda: self.on_act_del(musics))
        self.play_list_menu.exec(QCursor.pos())

    def on_act_del(self, musics: list):
        cur = self.parent().cur_play_list.get_current_music()
        playing = False
        for music in musics:
            if music.path == cur.path and music.mid == cur.mid:
                playing = True

        for music in musics:
            self.parent().cur_play_list.remove(music)
        self.show_data(self.parent().cur_play_list)
        self.parent().label_play_count.setText(str(self.parent().cur_play_list.size()))
        if playing:
            self.parent().next_music()

        # 若播放列表为空
        if self.parent().cur_play_list.size() == 0:
            self.parent().music_info_widget.hide()
            self.parent().stop_current()
            self.parent().btn_start.setStyleSheet("QPushButton{border-image:url(./resource/image/播放.png)}" +
                                                  "QPushButton:hover{border-image:url(./resource/image/播放2.png)}")

    def create_collect_menu(self, musics: list):
        self.collect_menu.clear()
        act0 = self.create_widget_action("./resource/image/添加歌单.png", "创建新歌单")
        self.collect_menu.addAction(act0)
        self.collect_menu.addSeparator()
        mls = list(filter(lambda ml: ml.id != MusicList.DEFAULT_ID, self.music_list_service.list_(MusicList())))
        for music_list in mls:
            act = self.create_widget_action("./resource/image/歌单.png", music_list.name, music_list)
            self.collect_menu.addAction(act)
            act.triggered.connect(lambda: self.parent().on_acts_choose(musics))

    def __init_ui(self):
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.tabWidget.setCurrentWidget(self.play_list)
        self.tabWidget.tabBar().setCursor(Qt.PointingHandCursor)
        self.tabWidget.setStyleSheet("QTabWidget::pane{border-top: 1px solid #e1e1e2;}" +
                                     "QTabWidget::tab-bar{alignment:center;height:46px;}" +
                                     "QTabBar::tab{height:26px;width:128px;border-radius:4px;}" +
                                     "QTabBar::tab:selected{background-color:#7c7d86;color:#ffffff;}" +
                                     "QTabBar::tab:!selected{background-color:#ffffff;color:#888888;}" +
                                     "QTabBar::tab:!selected:hover{background:#f5f5f7;color:#666666;}"
                                     )
        self.widget.setStyleSheet(
            "background:#f9f9f9;border:none;border-bottom:1px solid #efefef;border-left:1px solid #c3c3c4;")
        self.label.setStyleSheet("border:none")
        self.label_2.setStyleSheet("border:none")
        self.widget_2.setStyleSheet(
            "background:#f9f9f9;border:none;border-bottom:1px solid #efefef;border-left:1px solid #c3c3c4;")
        self.pushButton.setStyleSheet("QPushButton{color:#666666;border:none;}QPushButton:hover{color:#444444;}")
        self.pushButton_2.setStyleSheet("QPushButton{color:#666666;border:none;}QPushButton:hover{color:#444444;}")
        self.pushButton.setCursor(Qt.PointingHandCursor)
        self.pushButton_2.setCursor(Qt.PointingHandCursor)

        # 播放列表右键菜单
        self.play_list_menu = QMenu()
        # 鼠标移到收藏到歌单时的二级菜单
        self.collect_menu = QMenu()

        self.play_list_menu.setStyleSheet(
            "QMenu{background-color:#fafafc;border:1px solid #c8c8c8;font-size:13px;width:214px;}" +
            "QMenu::item {height:36px;padding-left:44px;padding-right:60px;}" +
            "QMenu::item:selected {background-color:#ededef;}" +
            "QMenu::separator{background-color:#ededef;height:1px}")
        self.collect_menu.setStyleSheet(
            "QMenu{background-color:#fafafc;border:1px solid #c8c8c8;font-size:13px;width:214px;}" +
            "QMenu::item {height:36px;padding-left:44px;padding-right:60px;}" +
            "QMenu::item:selected {background-color:#ededef;}" +
            "QMenu::separator{background-color:#ededef;height:1px}")

    def __init_table_widget_ui(self):
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["", "音乐标题", "歌手", "专辑", "时长"])
        self.tableWidget.horizontalHeader().setHidden(True)
        self.tableWidget.setStyleSheet("QTableWidget{border:none;border-left:1px solid #c0c0c1;background:#fafafa;}" +
                                       "QTableWidget::item::selected{background-color:#e3e3e5}")

    def __set_table_widget_width(self):
        self.tableWidget.setColumnWidth(0, self.width() * 0.03)
        self.tableWidget.setColumnWidth(1, self.width() * 0.63)
        self.tableWidget.setColumnWidth(2, self.width() * 0.17)
        self.tableWidget.setColumnWidth(3, self.width() * 0.05)
        self.tableWidget.setColumnWidth(4, self.width() * 0.12)

    def show_data(self, play_list):
        self.setGeometry(self.parent().width() - 580, 150, 580,
                         self.parent().height() - 150 - 48)
        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(play_list.size())
        self.label.setText("共%d首" % play_list.size())
        icon = QIcon("./resource/image/链接.png")

        for i in range(play_list.size()):
            self.btn_link = QLabel(self.tableWidget)
            self.btn_link.setStyleSheet("background-color:rgba(0,0,0,0)")
            self.btn_link.setPixmap(QPixmap("./resource/image/链接.png"))
            self.btn_link.setAlignment(Qt.AlignCenter)
            self.btn_link.setCursor(Qt.PointingHandCursor)
            # self.btn_link.installEventFilter(self)

            # icon_item = QTableWidgetItem()
            # icon_item.setIcon(icon)
            music = play_list.get(i)
            self.tableWidget.setItem(i, 0, QTableWidgetItem("\t"))
            self.tableWidget.setItem(i, 1, QTableWidgetItem(music.title))
            self.tableWidget.setItem(i, 2, QTableWidgetItem(music.artist))
            # self.tableWidget.setItem(i, 3, icon_item)
            self.tableWidget.setCellWidget(i, 3, self.btn_link)

            self.tableWidget.setItem(i, 4, QTableWidgetItem(util.format_time(music.duration)))

        # 为当前音乐设置喇叭图标
        icon_label = QLabel()
        icon_label.setPixmap(QPixmap("./resource/image/musics_play.png"))
        icon_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        icon_label.setCursor(Qt.PointingHandCursor)
        self.tableWidget.setCellWidget(play_list.get_current_index(), 0, icon_label)
        # 当行数等于13时, maximum=0, row=14->maximum = 1, row=15->maximum=2, row=16->maximum=3
        # 15-27
        # print("table widget height: ", self.tableWidget.height())
        # print("height: ", self.tableWidget.verticalScrollBar().height())
        # print("maximum: ", self.tableWidget.verticalScrollBar().maximum())
        # print("value:", self.tableWidget.verticalScrollBar().value())
        # print("position:", self.tableWidget.verticalScrollBar().sliderPosition())
        # self.tableWidget.verticalScrollBar().setSliderPosition(self.tableWidget.verticalScrollBar().maximum() / 2)

    def create_widget_action(self, icon, text, data=None):
        act = QWidgetAction(self)
        act.setText(text)
        if data is not None:
            act.setData(data)
        widget = QWidget(self)
        layout = QHBoxLayout()
        layout.setContentsMargins(13, -1, -1, 11)
        layout.setSpacing(13)
        lb_icon = QLabel(widget)
        lb_icon.resize(18, 18)
        lb_text = QLabel(text, widget)
        if icon != "":
            lb_icon.setPixmap(QPixmap(icon))
        widget.setStyleSheet("QWidget:hover{background:#ededef}" + ""
                                                                   "QWidget{color:#000000;font-size:13px;}")
        layout.addWidget(lb_icon)
        layout.addWidget(lb_text)
        layout.addStretch()
        widget.setLayout(layout)
        act.setDefaultWidget(widget)
        return act

    def eventFilter(self, QObject, QEvent_):
        # print(self.btn_link == QObject)

        if self.btn_link == QObject:
            if QEvent_.type() == QEvent.MouseButtonPress:
                # print("haha")
                item = self.tableWidget.currentItem()
                if item is not None:
                    pass
                    # print(item.row())
        return super().eventFilter(QObject, QEvent_)

    def paintEvent(self, QPaintEvent):
        # 画出边框线
        paint = QPainter()
        paint.begin(self)
        pen = QPen()
        pen.setColor(QColor("#c3c3c4"))
        paint.setPen(pen)
        paint.drawLine(0, 0, self.width(), 0)
        paint.drawLine(0, 0, 0, self.tabWidget.tabBar().height())

        # 画出头部背景
        brush = QtGui.QBrush(QColor("#f4f4f6"))
        brush.setStyle(Qt.SolidPattern)
        paint.setBrush(brush)
        paint.drawRect(0, 0, self.width(), self.tabWidget.tabBar().height())
