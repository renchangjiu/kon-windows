import os

from PyQt5.QtCore import Qt, QEvent, QSize, QModelIndex, QObject
from PyQt5.QtGui import QPixmap, QFont, QIcon, QImage, QFontMetrics, QCursor, QCloseEvent, QMouseEvent, QMovie, \
    QPaintEvent
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QListWidgetItem, QTableWidgetItem, \
    QAction, QMenu, QLabel, QWidgetAction, QHBoxLayout

from src.Apps import Apps
from src.common.QssHelper import QssHelper
from src.component.AddMusicListDialog import AddMusicListDialog
from src.component.Const import Const
from src.component.PlaylistDialog import PlayListDialog
from src.component.ScanPaths import ScanPaths
from src.component.ScannedPathsDialog import ScannedPathsDialog
from src.model.Music import Music
from src.model.MusicList import MusicList
from src.service.MP3Parser import MP3
from src.ui.MainWidgetUI import Ui_Form
from src.ui.Toast import Toast
from src.ui.style import Style
from src.util import util


class MainWindow(QWidget, Ui_Form):
    # 播放状态
    stopped_state = 0  # 该状态已被废弃
    playing_state = 1
    paused_state = 2

    def __init__(self):
        QWidget.__init__(self)
        Ui_Form.__init__(self)

        self.musicService = Apps.musicService
        self.musicListService = Apps.musicListService
        self.config = Apps.config
        self.player = Apps.player
        self.playlist = Apps.playlist
        # 音量
        self.volume = 50

        # 全屏播放界面的歌词label是否正在被滚动
        self.is_wheeling = False

        # 当前歌单的音乐列表, 初始化时加载歌单中所有音乐, 搜索时会清空音乐并加载搜索结果
        self.curMusicList = None
        # 包含当前歌单的全部音乐, 只用于搜索使用的库
        self.curWholeMusicList = None

        self.setupUi(self)

        self.init_menu()

        self.init_ui()
        self.initConnect()
        self.initShortcut()
        self.initData()
        self.initTableUi()
        self.min = self.scrollArea.verticalScrollBar().minimum()

        # 重新搜索本地音乐
        ScanPaths.scan(self.on_scan)

    def on_scan(self, state: int):
        if state == 1:
            self.label_search_gif = QLabel(self.navigation)
            movie = QMovie(Const.res + "/image/1.gif")
            self.label_search_gif.setMovie(movie)
            self.label_search_gif.setGeometry(160, 9, 16, 16)
            self.label_search_gif.show()
            movie.start()
            movie.setSpeed(90)
            self.label_search_state.setText("正在更新本地音乐列表...")
        else:
            self.label_search_gif.hide()
            self.label_search_state.setText("更新完成")
            self.reload_local_musics()

    def initData(self):
        self.navigation.setIconSize(QSize(18, 18))
        font = QFont()
        font.setPixelSize(13)
        local_item = QListWidgetItem(self.navigation)
        local_item.setData(Qt.UserRole, self.musicListService.get_local_music())
        local_item.setIcon(QIcon(Const.res + "/image/歌单0.png"))
        local_item.setText("本地音乐")
        local_item.setFont(font)

        self.navigation.addItem(local_item)

        item1 = QListWidgetItem()
        item1.setText("创建的歌单")
        item1.setFlags(Qt.NoItemFlags)
        self.navigation.addItem(item1)
        mls = list(filter(lambda ml: ml.id != MusicList.DEFAULT_ID, self.musicListService.list_(MusicList())))
        music_list_icon = QIcon(Const.res + "/image/歌单1.png")
        for music_list in mls:
            item = QListWidgetItem()
            item.setIcon(music_list_icon)
            item.setFont(font)
            item.setText(music_list.name)
            item.setData(Qt.UserRole, music_list)
            self.navigation.addItem(item)

        # 默认选中第一个歌单
        self.navigation.setCurrentRow(0)
        curMusicListId = self.navigation.currentItem().data(Qt.UserRole).id
        self.updateMusicList(curMusicListId)

        self.stackedWidget_2.setCurrentWidget(self.music_list_detail)
        self.musics.setColumnCount(5)
        # 将歌单中的歌曲列表加载到 table widget
        self.playlist.setMusics(self.curMusicList.musics)
        print(self.playlist)
        self.playlist.setIndex(0)
        self.show_musics_data()

    def initTableUi(self):
        # --------------------- 1. 歌单音乐列表UI --------------------- #
        self.musics.setHorizontalHeaderLabels(["", "音乐标题", "歌手", "专辑", "时长"])
        self.musics.setColumnCount(5)
        # --------------------- 2. 本地音乐页面UI--------------------- #
        self.tb_local_music.setHorizontalHeaderLabels(["", "音乐标题", "歌手", "专辑", "时长", "大小"])
        self.tb_local_music.setColumnCount(6)

    def onNavigationClicked(self, item: QListWidgetItem):
        """ 当点击左侧 navigation 时, 显示对应页面 """
        data = item.data(Qt.UserRole)
        if data is None:
            return

        if data.id == 0:
            self.show_local_music_page()
        else:
            cur_id = data.id
            self.updateMusicList(cur_id)
            self.stackedWidget_2.setCurrentWidget(self.music_list_detail)
            self.set_musics_layout()
            # 加载歌单中的歌曲列表
            self.show_musics_data()
            self.musics.setCurrentCell(0, 0)

    # 将歌单中的歌曲列表加载到 table widget(需先设置行列数)
    def show_musics_data(self):
        self.music_list_name.setText(self.curMusicList.name)
        self.music_list_date.setText("%s创建" % self.curMusicList.created)
        self.lb_music_count.setText("<p>歌曲数</p><p style='text-align: right'>%d</p>" % len(self.curMusicList.musics))
        self.lb_played_count.setText(
            "<p>播放数</p><p style='text-align: right'>%d</p>" % self.curMusicList.play_count)

        self.musics.clearContents()
        self.musics.setRowCount(len(self.curMusicList.musics))
        musics__ = self.curMusicList
        for i in range(len(musics__.musics)):
            music = musics__.get(i)
            item = QTableWidgetItem()
            item.setData(Qt.UserRole, music)
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item.setText(str(i + 1) + " ")
            self.musics.setItem(i, 0, item)
            item = QTableWidgetItem(str(music.title))
            item.setToolTip(music.title)
            self.musics.setItem(i, 1, item)
            item = QTableWidgetItem(music.artist)
            item.setToolTip(music.artist)
            self.musics.setItem(i, 2, item)
            item = QTableWidgetItem(music.album)
            item.setToolTip(music.album)
            self.musics.setItem(i, 3, item)
            item = QTableWidgetItem(util.format_time(music.duration))
            item.setToolTip(util.format_time(music.duration))
            self.musics.setItem(i, 4, item)

    # 展示本地音乐页面的表格数据
    def show_local_music_page_data(self):
        self.label_2.setText("%d首音乐" % len(self.curWholeMusicList.musics))
        self.tb_local_music.clearContents()
        self.tb_local_music.setRowCount(len(self.curMusicList.musics))
        self.set_tb_local_music_layout()
        for i in range(len(self.curMusicList.musics)):
            music = self.curMusicList.get(i)
            item = QTableWidgetItem()
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item.setText(str(i + 1) + " ")
            self.tb_local_music.setItem(i, 0, item)
            item = QTableWidgetItem(music.title)
            item.setToolTip(str(music.title))
            self.tb_local_music.setItem(i, 1, item)
            item = QTableWidgetItem(music.artist)
            item.setToolTip(str(music.artist))
            self.tb_local_music.setItem(i, 2, item)
            item = QTableWidgetItem(music.album)
            item.setToolTip(str(music.album))
            self.tb_local_music.setItem(i, 3, item)
            item = QTableWidgetItem(util.format_time(music.duration))
            item.setToolTip(util.format_time(music.duration))
            self.tb_local_music.setItem(i, 4, item)
            item = QTableWidgetItem(music.size)
            item.setToolTip(str(music.size))
            self.tb_local_music.setItem(i, 5, item)
        self.setIconItem()

    def setIconItem(self):
        """ 若当前播放的音乐属于该歌单, 则为其设置喇叭图标 """
        if self.playlist is None or self.playlist.getCurrentMusic() is None:
            return
        curMusic = self.playlist.getCurrentMusic()
        # 找到当前播放的音乐在该歌单中的索引
        row4playing = self.musicService.index_of(curMusic.id, self.curMusicList)
        if row4playing == -1:
            return
        iconLabel = QLabel()
        # 播放状态或暂停状态显示两种图标
        state = self.player.getState()
        if state == QMediaPlayer.PlayingState:
            iconLabel.setPixmap(QPixmap(Const.res + "/image/musics_play.png"))
        else:
            iconLabel.setPixmap(QPixmap(Const.res + "/image/musics_pause.png"))
        iconLabel.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        # 区分歌单页面和本地音乐页面
        if self.stackedWidget_2.currentWidget() == self.music_list_detail:
            self.musics.item(row4playing, 0).setText("")
            self.musics.setCellWidget(row4playing, 0, iconLabel)
        elif self.stackedWidget_2.currentWidget() == self.local_music_page:
            self.tb_local_music.item(row4playing, 0).setText("")
            self.tb_local_music.setCellWidget(row4playing, 0, iconLabel)

    def show_local_music_page(self):
        self.stackedWidget_2.setCurrentWidget(self.local_music_page)
        self.curMusicList = self.musicListService.get_local_music()
        self.curWholeMusicList = self.musicListService.get_local_music()
        self.show_local_music_page_data()

    def set_musics_layout(self):
        self.musics.setColumnWidth(0, self.musics.width() * 0.06)
        self.musics.setColumnWidth(1, self.musics.width() * 0.35)
        self.musics.setColumnWidth(2, self.musics.width() * 0.24)
        self.musics.setColumnWidth(3, self.musics.width() * 0.23)
        self.musics.setColumnWidth(4, self.musics.width() * 0.12)

    def set_tb_local_music_layout(self):
        self.tb_local_music.setColumnWidth(0, self.tb_local_music.width() * 0.05)
        self.tb_local_music.setColumnWidth(1, self.tb_local_music.width() * 0.37)
        self.tb_local_music.setColumnWidth(2, self.tb_local_music.width() * 0.22)
        self.tb_local_music.setColumnWidth(3, self.tb_local_music.width() * 0.22)
        self.tb_local_music.setColumnWidth(4, self.tb_local_music.width() * 0.07)
        self.tb_local_music.setColumnWidth(5, self.tb_local_music.width() * 0.07)

    def showMusicInfo(self):
        """ 显示左下音乐名片相关信息 """
        if self.playlist.isEmpty():
            self.music_info_widget.hide()
            return
        if self.music_info_widget.isHidden():
            self.music_info_widget.show()
        music = self.playlist.getCurrentMusic()
        image_data = MP3(music.path).image
        if image_data == b"":
            image = QPixmap(Const.res + "/image/default_music_image.png")
        else:
            image = QPixmap.fromImage(QImage.fromData(image_data))
        max_width = 110
        title = music.title
        artist = music.artist
        self.btn_music_image.setIcon(QIcon(image))

        self.label_music_title.setText(self.get_elided_text(self.label_music_title.font(), title, max_width))
        self.label_music_artist.setText(self.get_elided_text(self.label_music_artist.font(), artist, max_width))

    def initButton(self):
        self.btn_previous.setCursor(Qt.PointingHandCursor)
        self.btn_next.setCursor(Qt.PointingHandCursor)
        self.btn_start.setCursor(Qt.PointingHandCursor)
        self.btn_mute.setCursor(Qt.PointingHandCursor)
        self.btn_play_mode.setCursor(Qt.PointingHandCursor)
        self.btn_play_list.setCursor(Qt.PointingHandCursor)
        self.btn_desktop_lyric.setCursor(Qt.PointingHandCursor)

    def initConnect(self):
        self.installEventFilter(self)
        # header
        self.header.installEventFilter(self)
        self.btn_window_close.clicked.connect(self.close)
        self.btn_window_min.clicked.connect(self.showMinimized)
        self.btn_window_max.clicked.connect(self.showMaximizedNormal)
        self.btn_icon.clicked.connect(lambda: self.main_stacked_widget.setCurrentWidget(self.main_page))

        # nav
        self.btn_zoom.installEventFilter(self)
        self.btn_music_image.installEventFilter(self)
        self.music_image_label.installEventFilter(self)
        self.navigation.itemClicked.connect(self.onNavigationClicked)
        self.btn_music_image.clicked.connect(self.change2playPage)
        self.navigation.customContextMenuRequested.connect(self.onNavigationRightClicked)  # 右键菜单
        self.btn_add_music_list.clicked.connect(lambda: AddMusicListDialog.show_(self, self.positive))

        # footer
        # 歌词滚动
        # self.label_lyric.installEventFilter(self)
        self.btn_start.clicked.connect(self.play)
        self.btn_mute.clicked.connect(self.setMute)
        self.btn_next.clicked.connect(self.nextMusic)
        self.btn_previous.clicked.connect(self.previousMusic)
        self.btn_play_list.clicked.connect(self.togglePlayListDialog)
        self.slider_volume.valueChanged.connect(self.setVolume)
        self.slider_progress.sliderReleased.connect(self.seekMusic)

        # playlist
        self.playlist.changed.connect(self.onPlaylistChanged)

        # musics
        self.musics.doubleClicked.connect(self.onTableDoubleclick)
        self.le_search_music_list.textChanged.connect(self.on_search)
        self.musics.customContextMenuRequested.connect(self.onMusicsRightClicked)

        # 全屏播放页面
        self.btn_return.clicked.connect(lambda: self.main_stacked_widget.setCurrentWidget(self.main_page))

        # 本地音乐页面
        self.le_search_local_music.textChanged.connect(self.on_search)
        self.tb_local_music.doubleClicked.connect(self.onTableDoubleclick)
        self.btn_choose_dir.clicked.connect(lambda: ScannedPathsDialog.show_(self))
        self.tb_local_music.customContextMenuRequested.connect(self.on_tb_local_music_right_click)  # 右键菜单

        # player
        self.player.stateChanged.connect(self.onStateChanged)
        self.player.mutedChanged.connect(self.onMutedChanged)
        self.player.positionChanged.connect(self.onPositionChanged)
        self.player.mediaStatusChanged.connect(self.onMediaStatusChanged)

    def initShortcut(self):
        pause_play_act = QAction(self)
        pause_play_act.setShortcut(Qt.Key_Space)
        self.addAction(pause_play_act)
        pause_play_act.triggered.connect(self.play)

    def eventFilter(self, obj: QObject, event: QEvent):
        if event.type() == QEvent.MouseButtonPress:
            if not self.playlistDialog.isHidden():
                self.playlistDialog.hide()
        # 1. 如果主窗口被激活, 关闭子窗口
        if event.type() == QEvent.WindowActivate:
            if not self.playlistDialog.isHidden():
                self.playlistDialog.hide()

        # 2. 如果左下缩放按钮被鼠标左键拖动, 则缩放窗口
        if obj == self.btn_zoom and event.type() == QEvent.MouseMove and event.buttons() == Qt.LeftButton:
            width = event.globalX() - self.x()
            height = event.globalY() - self.y()
            self.setGeometry(self.x(), self.y(), width, height)
        if obj == self.header and type(event) == QMouseEvent and event.buttons() == Qt.LeftButton:
            # 如果标题栏被双击
            if event.type() == QEvent.MouseButtonDblClick:
                self.showMaximizedNormal()
            # 记录拖动标题栏的位置
            elif event.type() == QEvent.MouseButtonPress:
                self.point = event.globalPos() - self.frameGeometry().topLeft()
            # 如果标题栏被拖动
            elif event.type() == QEvent.MouseMove:
                if self.windowState() == Qt.WindowNoState:
                    self.move(event.globalPos() - self.point)
        # 3. 当鼠标移动到music_image时显示遮罩层
        if obj == self.btn_music_image:
            if event.type() == QEvent.Enter:
                self.music_image_label.setGeometry(self.btn_music_image.geometry())
                self.music_image_label.show()
        if obj == self.music_image_label:
            if event.type() == QEvent.Leave:
                self.music_image_label.hide()
            if event.type() == QEvent.MouseButtonPress:
                self.change2playPage()
        # 4.
        if obj == self.label_lyric:
            if event.type() == QEvent.Wheel:
                self.is_wheeling = True
            else:
                self.is_wheeling = False
        return super().eventFilter(obj, event)

    def showMaximizedNormal(self):
        state = self.windowState()
        if state == Qt.WindowNoState:
            self.setWindowState(Qt.WindowMaximized)
            self.btn_window_max.setStyleSheet("QPushButton{border-image:url(./resource/image/恢复最大化.png)}" +
                                              "QPushButton:hover{border-image:url(./resource/image/恢复最大化2.png)}")
        else:
            self.setWindowState(Qt.WindowNoState)
            self.btn_window_max.setStyleSheet("QPushButton{border-image:url(./resource/image/maximize.png)}" +
                                              "QPushButton:hover{border-image:url(./resource/image/maximize_hover.png)}")

    # 使播放的相关信息复位
    def infoReset(self):
        self.label_pos.setText("00:00")
        self.label_duration.setText("00:00")
        self.slider_progress.setValue(0)

    def change2playPage(self):
        self.main_stacked_widget.setCurrentWidget(self.play_page)

    def paintEvent(self, event: QPaintEvent):
        self.btn_zoom.setGeometry(self.width() - 18, self.height() - 18, 14, 14)
        self.set_tb_local_music_layout()
        if self.curMusicList is not None:
            self.set_musics_layout()

    def init_ui(self):
        self.setWindowIconText("qaq")
        self.setWindowIcon(QIcon(Const.rp("/image/app-icon.png")))

        # font = QFont("Consolas", 10, 50)
        # self.musics.setFont(font)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.main_stacked_widget.setCurrentWidget(self.main_page)
        self.stackedWidget_2.setCurrentWidget(self.music_list_detail)
        # ------------------ header------------------ #
        self.search_act = QAction(self)
        self.search_act.setIcon(QIcon(Const.res + "/image/搜索3.png"))
        self.le_search.addAction(self.search_act, QLineEdit.TrailingPosition)

        # ------------------ 右上歌单相关信息------------------ #
        mln_font = QFont()
        mln_font.setPointSize(20)
        self.music_list_name.setFont(mln_font)
        self.music_list_image.setPixmap(QPixmap(Const.res + "/image/music_list/rikka.png"))
        self.search_act = QAction(self)
        self.search_act.setIcon(QIcon(Const.res + "/image/搜索3.png"))
        self.le_search_music_list.addAction(self.search_act, QLineEdit.TrailingPosition)

        # # ------------------ 左边导航栏 ------------------ #
        self.slider_progress.setCursor(Qt.PointingHandCursor)
        # 创建歌单按钮
        self.btn_add_music_list = QPushButton(self.navigation)
        self.btn_add_music_list.setObjectName("btn_add_music_list")
        self.btn_add_music_list.setCursor(Qt.PointingHandCursor)
        self.btn_add_music_list.setGeometry(160, 39, 18, 18)

        # ------------------ 左下音乐名片模块 ------------------ #
        self.music_image_label = QLabel(self.music_info_widget)
        Style.init_music_card_style(self.music_info_widget, self.btn_music_image, self.music_image_label)
        self.showMusicInfo()

        # ------------------ footer ------------------ #
        # 右下窗口缩放按钮
        self.btn_zoom = QPushButton(self)
        Style.init_footer_style(self.slider_volume, self.footer, self.volume, self.btn_zoom, self.width(),
                                self.height())

        # ------------------ 全屏播放窗口 ------------------ #
        self.play_page.setStyleSheet("border-image:url(./resource/image/渐变背景.png) repeated;border:none; ")
        self.label_title.setStyleSheet("border-image:none")
        self.label_album.setStyleSheet("border-image:none")
        self.label_artist.setStyleSheet("border-image:none")
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.verticalScrollBar().setStyleSheet("QScrollBar{background:#fafafa;width:10px;border:none}"
                                                          "QScrollBar::handle{background-color:#e1e1e2; border:none;}"
                                                          "QScrollBar::handle:hover{background:#adb0b4;}"
                                                          "QScrollBar::sub-line{background-color:#e1e1e2;}"
                                                          "QScrollBar::add-line{background-color:#e1e1e2}"
                                                          "QScrollBar::add-page{background-color:#ebebe9;}"
                                                          "QScrollBar::sub-page{background-color:#ebebe9;}")
        self.btn_return.setStyleSheet(
            "QPushButton{border-image:url(./resource/image/取消全屏.png);border-radius:5px;border-color:#dadadb}" +
            "QPushButton:hover{border-image:url(./resource/image/取消全屏2.png)}")
        self.btn_return.setCursor(Qt.PointingHandCursor)
        s = "<p>111阿斯蒂芬</p><br/><p>222发个好豆腐干</p><br/><p>333地方活佛济公</p><br/><p>444打成供东方红</p><br/><p>555宽高画更健康换个</p><br/>" \
            # min 总是0
        min = self.scrollArea.verticalScrollBar().minimum()
        _max = self.scrollArea.verticalScrollBar().maximum()
        print(min)
        print(self.scrollArea.verticalScrollBar().maximum())
        self.label_lyric.setText(s)

        # 右下播放列表页面
        self.playlistDialog = PlayListDialog(self)
        # 本地音乐页面
        self.widget.setStyleSheet("QWidget#widget{background-color:#fafafa;border:none;}")
        self.search_act_2 = QAction(self)
        self.search_act_2.setIcon(QIcon(Const.res + "/image/搜索3.png"))
        self.le_search_local_music.addAction(self.search_act_2, QLineEdit.TrailingPosition)
        self.initButton()
        self.setStyleSheet(QssHelper.load("/main/content.css"))
        self.header.setStyleSheet(QssHelper.load("/main/header.css"))
        self.navigation.setStyleSheet(QssHelper.load("/main/navigation.css"))

    def init_menu(self):
        # 1. 导航栏右键菜单
        self.nav_menu = QMenu()

        # 2. 在音乐列表上右键的菜单
        self.musics_menu = QMenu()

        # 3. 鼠标移到收藏到歌单时的二级菜单
        self.collect_menu = QMenu()

        # 4. 本地音乐右键菜单
        self.lm_menu = QMenu()

        qss = "QMenu{background-color:#fafafc;border:1px solid #c8c8c8;font-size:13px;width:214px;}" \
              "QMenu::item {height:36px;padding-left:44px;padding-right:60px;}" \
              "QMenu::item:selected {background-color:#ededef;}" \
              "QMenu::separator{background-color:#ededef;height:1px}"
        self.nav_menu.setStyleSheet(qss)
        self.musics_menu.setStyleSheet(qss)
        self.collect_menu.setStyleSheet(qss)
        self.lm_menu.setStyleSheet(qss)

    def togglePlayListDialog(self):
        if self.playlistDialog.isHidden():
            self.playlistDialog.show()
        else:
            self.playlistDialog.hide()

    def positive(self, text):
        """ 新增歌单 """
        self.musicListService.insert(text)
        self.navigation.clear()
        self.initData()

    # 显示nav右键菜单
    def onNavigationRightClicked(self, pos):
        item = self.navigation.itemAt(pos)
        data = item.data(Qt.UserRole)
        if type(data) == MusicList and data.id != 0 and data.name != "本地音乐":
            self.nav_menu.clear()
            act1 = self.create_widget_action("./resource/image/nav-播放.png", "播放(Enter)")
            act2 = self.create_widget_action("./resource/image/导出.png", "导出歌单")
            act3 = self.create_widget_action("./resource/image/编辑.png", "编辑歌单信息(E)")
            act4 = self.create_widget_action("./resource/image/删除.png", "删除歌单(Delete)")
            act4.triggered.connect(lambda: self.del_music_list(data))

            self.nav_menu.addAction(act1)
            self.nav_menu.addAction(act2)
            self.nav_menu.addSeparator()
            self.nav_menu.addAction(act3)
            self.nav_menu.addAction(act4)
            self.nav_menu.exec(QCursor.pos())

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
        widget.setStyleSheet("QWidget:hover{background:#ededef}")
        layout.addWidget(lb_icon)
        layout.addWidget(lb_text)
        layout.addStretch()
        widget.setLayout(layout)
        act.setDefaultWidget(widget)
        return act

    def onMusicsRightClicked(self, pos):
        self.musics_menu.clear()
        act1 = self.create_widget_action("./resource/image/nav-播放.png", "播放(Enter)")
        act2 = self.create_widget_action("./resource/image/nav-下一首播放.png", "下一首播放(Enter)")
        act3 = QAction("收藏到歌单(Ctrl+S)", self)
        act4 = self.create_widget_action("./resource/image/打开文件.png", "打开文件所在目录")
        act5 = self.create_widget_action("./resource/image/删除.png", "从歌单中删除(Delete)")

        self.musics_menu.addAction(act1)
        self.musics_menu.addAction(act2)
        self.musics_menu.addAction(act3)
        # 获取被选中的行, 包括列
        items = self.musics.selectedItems()
        # 去重, 获取被选中的行号
        rows = set()
        for item in items:
            rows.add(item.row())
        # 被选中的音乐
        musics = []
        for row in rows:
            music = self.curMusicList.get(row)
            musics.append(music)

        # 设置子菜单归属于act3
        self.create_collect_menu(musics)
        act3.setMenu(self.collect_menu)
        self.musics_menu.addMenu(self.collect_menu)
        # 只选中了一行
        if len(rows) == 1:
            self.musics_menu.addSeparator()
            self.musics_menu.addAction(act4)
        else:
            self.musics_menu.addSeparator()
        self.musics_menu.addAction(act5)
        act1.triggered.connect(lambda: self.on_act_play(musics))
        act2.triggered.connect(lambda: self.on_act_next_play(musics))
        act4.triggered.connect(lambda: self.on_act_open_file(musics))
        act5.triggered.connect(lambda: self.on_act_del(musics))
        self.musics_menu.exec(QCursor.pos())

    # 当存放音乐列表的表格被双击
    def onTableDoubleclick(self, modelIndex: QModelIndex):
        index = modelIndex.row()
        # 把当前歌单的全部音乐加入到播放列表
        self.playlist.setMusics(self.curMusicList.musics)
        # 找到被双击的音乐在 cur_whole_music_list 中的索引
        self.playlist.setIndex(index)
        self.musics.selectRow(index)
        self.play()

    def on_act_play(self, musics: list):
        """
        选中歌单列表的音乐, 点击 "播放"
            1. 若选中的音乐已在播放列表中, 则移除已存在的, 然后重新加入
            2. 选中的音乐依次在 currentIndex 后加入播放列表
            3. 播放第一个选中的音乐
        """
        self.playlist.remove(musics)
        index = self.playlist.getIndex()
        for music in musics:
            index += 1
            self.playlist.insert(index, music)

        self.playlist.setIndex(self.playlist.getIndex() + 1)
        # TODO: 若歌曲文件不存在
        # if not os.path.exists(self.playlist.getCurrentMusic().path):
        self.play()

    def on_act_next_play(self, musics: list):
        """
        选中歌单列表的音乐, 点击 "下一首播放"
            1. 若选中的音乐已在播放列表中, 则移除已存在的, 然后重新加入
            2. 选中的音乐依次在current index后加入播放列表
        """
        self.playlist.remove(musics)
        index = self.playlist.getIndex()
        for music in musics:
            index += 1
            self.playlist.insert(index, music)

    def create_collect_menu(self, musics: list):
        self.collect_menu.clear()
        act0 = self.create_widget_action("./resource/image/添加歌单.png", "创建新歌单")
        self.collect_menu.addAction(act0)
        self.collect_menu.addSeparator()
        mls = list(filter(lambda ml: ml.id != MusicList.DEFAULT_ID, self.musicListService.list_(MusicList())))
        for music_list in mls:
            act = self.create_widget_action("./resource/image/歌单.png", music_list.name, music_list)
            self.collect_menu.addAction(act)
            act.triggered.connect(lambda: self.on_acts_choose(musics))

    def on_acts_choose(self, musics: list):
        # 1. 在目标歌单的末尾加入; 2. 已存在的音乐则不加入(根据path判断)
        sender = self.sender()
        # data 是被选择的歌单对象, 但是该对象不包含所属音乐
        data = sender.data()
        target_music_list = self.musicListService.get(data.id)
        is_all_in = True
        insert_musics = []
        for music in musics:
            if not self.musicService.contains(target_music_list.id, music.path):
                is_all_in = False
                music.mid = target_music_list.id
                insert_musics.append(music)
        self.musicService.batch_insert(insert_musics)
        if not is_all_in:
            Toast.show_(self, "已收藏到歌单", True, 2000)
        else:
            Toast.show_(self, "歌曲已存在!", False, 2000)

    # 选中歌单列表的音乐, 点击 "打开文件所在目录"
    def on_act_open_file(self, musics: list):
        if len(musics) == 1:
            music = musics[0]
            command = "explorer /select, \"%s\"" % music.path.replace("/", "\\")
            os.system(command)

    # 选中歌单列表的音乐, 点击 "从歌单中删除"
    def on_act_del(self, musics: list):
        self.musicService.batch_delete(list(map(lambda m: m.id, musics)))
        self.updateMusicList()
        self.show_musics_data()
        # 清除已选择的项
        self.musics.clearSelection()

    def on_act_del_from_disk(self, musics: list):
        """ 从硬盘上删除本地音乐 """
        # 1.从歌单删除(本地音乐)
        # 2.从播放列表中删除(如果有的话)
        # 3.从硬盘删除
        self.musicService.batch_delete(list(map(lambda m: m.id, musics)))
        for music in musics:
            os.remove(music.path)
            self.playlist.remove(music)
        self.updateMusicList()
        self.show_local_music_page_data()
        # 清除已选择的项
        self.tb_local_music.clearSelection()

    # 本地音乐页面表格被右击
    def on_tb_local_music_right_click(self, pos):
        self.lm_menu.clear()
        act1 = self.create_widget_action("./resource/image/nav-播放.png", "播放(Enter)")
        act2 = self.create_widget_action("./resource/image/nav-下一首播放.png", "下一首播放(Enter)")
        act3 = QAction("收藏到歌单(Ctrl+S)", self)
        act4 = self.create_widget_action("./resource/image/打开文件.png", "打开文件所在目录")
        act5 = self.create_widget_action("./resource/image/删除.png", "从本地磁盘删除")

        self.lm_menu.addAction(act1)
        self.lm_menu.addAction(act2)
        self.lm_menu.addAction(act3)

        # 获取被选中的行, 包括列
        items = self.tb_local_music.selectedItems()
        # 被选中的行号
        rows = set()
        for item in items:
            rows.add(item.row())
        musics = []
        for row in rows:
            music = self.curMusicList.get(row)
            musics.append(music)
        # 设置子菜单归属于act3
        self.create_collect_menu(musics)
        act3.setMenu(self.collect_menu)
        self.lm_menu.addMenu(self.collect_menu)

        # 只选中了一行
        if len(rows) == 1:
            self.lm_menu.addSeparator()
            self.lm_menu.addAction(act4)
        else:
            self.lm_menu.addSeparator()
        self.lm_menu.addAction(act5)
        act1.triggered.connect(lambda: self.on_act_play(musics))
        act2.triggered.connect(lambda: self.on_act_next_play(musics))
        act4.triggered.connect(lambda: self.on_act_open_file(musics))
        act5.triggered.connect(lambda: self.on_act_del_from_disk(musics))
        self.lm_menu.exec(QCursor.pos())

    def onStateChanged(self, state: int):
        """ 当播放状态变化 """
        if state == QMediaPlayer.PlayingState:
            css = "QPushButton{border-image:url(./resource/image/btnPlayingState.png)}" \
                  "QPushButton:hover{border-image:url(./resource/image/btnPlayingStateHover.png)}"
        else:
            css = "QPushButton{border-image:url(./resource/image/btnPausedState.png)}" \
                  "QPushButton:hover{border-image:url(./resource/image/btnPausedStateHover.png)}"
        self.btn_start.setStyleSheet(css)
        self.setIconItem()
        self.infoReset()
        self.showMusicInfo()
        print("stateChanged")

    def onPositionChanged(self, position: int):
        duration = self.player.getDuration()
        if duration == 0:
            return
        # 进度条
        pos = int(float(position) / duration * 100)
        if not self.slider_progress.isSliderDown():
            self.slider_progress.setValue(pos)

        # duration label
        format_duration = util.format_time(int(duration / 1000))
        self.label_duration.setText(format_duration)

        # position label
        position = util.format_time(int(position / 1000))
        self.label_pos.setText(position)

    def onMutedChanged(self):
        """ 当静音状态改变 """
        muted = self.player.getMuted()
        css = ""
        if muted:
            css = "QPushButton{border-image:url(./resource/image/btnMuted.png)}" \
                  "QPushButton:hover{border-image:url(./resource/image/btnMutedHover.png)}"
        else:
            css = "QPushButton{border-image:url(./resource/image/btnNotMuted.png)}" \
                  "QPushButton:hover{border-image:url(./resource/image/btnNotMutedHover.png)}"
        self.btn_mute.setStyleSheet(css)

    def onMediaStatusChanged(self, mediaStatus: int):
        """ 当媒体状态变化 """
        if mediaStatus == QMediaPlayer.EndOfMedia:
            # 播放已到达当前媒体的结尾
            self.musicListService.play_count_incr(self.curMusicList.id)
            self.updateMusicList()
            self.lb_played_count.setText(
                "<p>播放数</p><p style='text-align: right'>%d</p>" % self.curMusicList.play_count)
            self.nextMusic()
        print("mediaStatusChanged")

    def del_music_list(self, music_list: MusicList):
        """ 删除歌单 """
        self.musicListService.logic_delete(music_list.id)
        self.navigation.clear()
        self.initData()

    def on_search(self, text: str):
        text = text.strip()
        self.curMusicList = self.musicService.search(text, self.curMusicList.id)
        # 显示当前页面显示两个不同的表格
        if self.stackedWidget_2.currentWidget() == self.music_list_detail:
            self.show_musics_data()
        elif self.stackedWidget_2.currentWidget() == self.local_music_page:
            self.show_local_music_page_data()

    def onPlaylistChanged(self):
        if self.stackedWidget_2.currentWidget() == self.music_list_detail:
            self.show_musics_data()
        elif self.stackedWidget_2.currentWidget() == self.local_music_page:
            self.show_local_music_page_data()
        self.label_play_count.setText(str(self.playlist.size()))
        if self.playlist.isEmpty():
            self.music_info_widget.hide()
        self.showMusicInfo()
        print("onPlaylistChanged")

    # 当改变了本地音乐的搜索路径, 重新读取本地音乐文件
    def reload_local_musics(self):
        self.curMusicList = self.musicListService.get_local_music()
        self.curWholeMusicList = self.musicListService.get_local_music()
        self.show_local_music_page_data()

    def play(self):
        self.player.play(self.playlist.getCurrentMusic())

    # 设置音量
    def setVolume(self, value: int):
        self.player.setVolume(value)

    def get_elided_text(self, font: QFont, _str: str, max_width: int):
        fm = QFontMetrics(font)
        # 计算字符串宽度
        w = fm.width(_str)
        # 当字符串宽度大于最大宽度时进行转换
        if w < max_width:
            return _str
        else:
            return self.sub(_str, max_width, fm)

    def sub(self, s, max_width, fm):
        w = fm.width(s)
        if w < max_width:
            return s + "..."
        else:
            return self.sub(s[0:-1], max_width, fm)

    def lrc_scroll(self, lrc, time):
        self.scrollArea.verticalScrollBar().setValue(self.min)
        self.min += 1
        print(self.scrollArea.verticalScrollBar().maximum())
        pass

    def previousMusic(self):
        if self.playlist.isEmpty():
            return
        self.playlist.previous()
        self.play()
        # TODO: 若歌曲文件不存在

    def nextMusic(self):
        if self.playlist.isEmpty():
            return
        self.playlist.next()
        self.play()
        # TODO: 若歌曲文件不存在

    def seekMusic(self):
        """ 定位到音乐的指定绝对位置, 秒 """
        duration = self.player.getDuration()
        if duration == 0:
            self.slider_progress.setValue(0)
            return
        pos = self.slider_progress.value() / 100 * duration
        self.player.setPosition(pos)

    def setMute(self):
        """ 设置静音 """
        self.player.toggleMuted()

    def updateMusicList(self, mid=None):
        """ 当歌单内音乐增加或被删除后, 需要更新相关变量 """
        if mid is not None:
            self.curMusicList = self.musicListService.get(mid)
            self.curWholeMusicList = self.musicListService.get(mid)
        else:
            self.curMusicList = self.musicListService.get(
                self.curMusicList.id)
            self.curWholeMusicList = self.musicListService.get(
                self.curMusicList.id)

    def closeEvent(self, event: QCloseEvent):
        self.player.stop()
# 1184
