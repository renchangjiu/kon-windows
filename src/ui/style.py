from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QSlider, QWidget, QLabel, QPushButton

from src.common.QssHelper import QssHelper


class Style(object):

    @staticmethod
    def init_footer_style(slider_volume: QSlider, footer: QWidget, volume: int, btn_zoom: QPushButton, width: int,
                          height: int):
        # ------------------ footer ------------------ #
        slider_volume.setValue(volume)
        footer.setStyleSheet(QssHelper.load("/main/footer.css"))
        btn_zoom.setGeometry(width - 18, height - 18, 14, 14)
        btn_zoom.setStyleSheet("QPushButton{border-image:url(./resource/image/缩放.png)}")
        btn_zoom.setCursor(Qt.SizeFDiagCursor)

    @staticmethod
    def init_music_card_style(music_info_widget: QWidget, btn_music_image: QPushButton, music_image_label: QLabel):
        music_info_widget.setStyleSheet(
            "QWidget#music_info_widget{background-color:#f5f5f7;border:none;border-right:1px solid #e1e1e2;}")
        music_info_widget.setCursor(Qt.PointingHandCursor)
        btn_music_image.setIconSize(QSize(44, 44))
        btn_music_image.setAutoFillBackground(True)
        music_image_label.setStyleSheet("QLabel{background-color: rgba(71, 71, 71, 150)}")
        music_image_label.setPixmap(QPixmap("./resource/image/全屏.png"))
        music_image_label.hide()
