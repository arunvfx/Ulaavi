# -*- coding: utf-8 -*-

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
import os


class Ui_Settings(QFrame):
    def __init__(self):
        super(Ui_Settings, self).__init__()
        self.resize(1637, 996)
        self.setObjectName("frame_settings")
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Plain)
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setSpacing(3)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(6, 6, 6, 6)
        font = QFont()
        font.setPointSize(9)

        self.group_settings_general = QGroupBox(self)
        self.group_settings_general.setObjectName("group_settings_general")
        self.group_settings_general.setFlat(True)
        self.verticalLayout_2 = QVBoxLayout(self.group_settings_general)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(10, 30, -1, -1)
        self.gridLayout = QGridLayout()
        self.gridLayout.setSpacing(9)
        self.gridLayout.setObjectName("gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.gridLayout.setContentsMargins(0, -1, -1, -1)
        self.threadsLabel = QLabel(self.group_settings_general)
        self.threadsLabel.setObjectName("threadsLabel")
        self.threadsLabel.setMaximumSize(QSize(100, 24))
        self.threadsLabel.setFont(font)
        self.threadsLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.threadsLabel, 3, 0, 1, 1)

        self.always_on_top_label = QLabel(self.group_settings_general)
        self.always_on_top_label.setObjectName("always_on_top_label")
        self.always_on_top_label.setMaximumSize(QSize(100, 24))
        self.always_on_top_label.setFont(font)
        self.always_on_top_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.always_on_top_label, 4, 0, 1, 1)

        self.ffmpeg_label = QLabel('FFmpeg', self.group_settings_general)
        self.ffmpeg_label.setObjectName("ffmpeg_label")
        self.ffmpeg_label.setMaximumSize(QSize(100, 24))
        self.ffmpeg_label.setFont(font)
        self.ffmpeg_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.gridLayout.addWidget(self.ffmpeg_label, 0, 0, 1, 1)

        self.ffmpegLineEdit = QLineEdit(self.group_settings_general)
        self.ffmpegLineEdit.setObjectName("ffmpegLineEdit")
        self.ffmpegLineEdit.setMinimumSize(QSize(0, 24))
        self.ffmpegLineEdit.setMaximumSize(QSize(600, 24))
        self.ffmpegLineEdit.setFont(font)
        self.ffmpegLineEdit.setFocusPolicy(Qt.ClickFocus)
        self.ffmpegLineEdit.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.ffmpegLineEdit, 0, 1, 1, 1)

        self.btn_browse_ffmpeg = QPushButton(self.group_settings_general)
        self.btn_browse_ffmpeg.setObjectName("btn_browse_proxy")
        self.btn_browse_ffmpeg.setMinimumSize(QSize(24, 24))
        self.btn_browse_ffmpeg.setMaximumSize(QSize(24, 24))
        self.btn_browse_ffmpeg.setFocusPolicy(Qt.NoFocus)

        self.gridLayout.addWidget(self.btn_browse_ffmpeg, 0, 2, 1, 1)

        self.jsonLineEdit = QLineEdit(self.group_settings_general)
        self.jsonLineEdit.setObjectName("jsonLineEdit")
        self.jsonLineEdit.setMinimumSize(QSize(0, 24))
        self.jsonLineEdit.setMaximumSize(QSize(600, 24))
        self.jsonLineEdit.setFont(font)
        self.jsonLineEdit.setFocusPolicy(Qt.ClickFocus)
        self.jsonLineEdit.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.jsonLineEdit, 2, 1, 1, 1)

        self.always_top_chkbox = QCheckBox('', self.group_settings_general)
        self.always_top_chkbox.setFont(font)
        self.always_top_chkbox.setFocusPolicy(Qt.ClickFocus)
        self.gridLayout.addWidget(self.always_top_chkbox, 4, 1, 1, 1)

        # self.lineEdit_thumbnail = QLineEdit(self.group_settings_general)
        # self.lineEdit_thumbnail.setObjectName("lineEdit_thumbnail")
        # self.lineEdit_thumbnail.setMaximumSize(QSize(80, 24))
        # self.lineEdit_thumbnail.setFont(font)
        # self.lineEdit_thumbnail.setFocusPolicy(Qt.ClickFocus)
        #
        # self.gridLayout.addWidget(self.lineEdit_thumbnail, 4, 1, 1, 1)

        self.proxyLineEdit = QLineEdit(self.group_settings_general)
        self.proxyLineEdit.setObjectName("proxyLineEdit")
        self.proxyLineEdit.setMaximumSize(QSize(600, 24))
        self.proxyLineEdit.setFont(font)
        self.proxyLineEdit.setFocusPolicy(Qt.ClickFocus)

        self.gridLayout.addWidget(self.proxyLineEdit, 1, 1, 1, 1)

        self.lineEdit_threads = QLineEdit(self.group_settings_general)
        self.lineEdit_threads.setObjectName("lineEdit_threads")
        self.lineEdit_threads.setMaximumSize(QSize(80, 24))
        self.lineEdit_threads.setFont(font)
        self.lineEdit_threads.setFocusPolicy(Qt.ClickFocus)

        self.gridLayout.addWidget(self.lineEdit_threads, 3, 1, 1, 1)

        self.cache_label = QLabel('Image Seqeuence', self.group_settings_general)
        self.cache_label.setFont(font)
        self.gridLayout.addWidget(self.cache_label, 5, 0, 1, 1)
        self.cache_label.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.cache_image_sequence = QCheckBox('', self.group_settings_general)
        self.cache_image_sequence.setFont(font)
        self.cache_image_sequence.setFocusPolicy(Qt.ClickFocus)
        self.gridLayout.addWidget(self.cache_image_sequence, 5, 1, 1, 1)

        self.proxyLabel = QLabel(self.group_settings_general)
        self.proxyLabel.setObjectName("proxyLabel")
        self.proxyLabel.setMaximumSize(QSize(100, 16777215))
        self.proxyLabel.setFont(font)
        self.proxyLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.proxyLabel, 1, 0, 1, 1)

        self.jsonLabel = QLabel(self.group_settings_general)
        self.jsonLabel.setObjectName("jsonLabel")
        self.jsonLabel.setMaximumSize(QSize(100, 24))
        self.jsonLabel.setFont(font)
        self.jsonLabel.setAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)

        self.gridLayout.addWidget(self.jsonLabel, 2, 0, 1, 1)

        self.btn_browse_proxy = QPushButton(self.group_settings_general)
        self.btn_browse_proxy.setObjectName("btn_browse_proxy")
        self.btn_browse_proxy.setMinimumSize(QSize(24, 24))
        self.btn_browse_proxy.setMaximumSize(QSize(24, 24))
        self.btn_browse_proxy.setFocusPolicy(Qt.NoFocus)

        self.gridLayout.addWidget(self.btn_browse_proxy, 1, 2, 1, 1)

        self_dummy = QFrame(self.group_settings_general)
        self_dummy.setObjectName("frame_settings_dummy")
        self_dummy.setFrameShape(QFrame.NoFrame)
        self_dummy.setFrameShadow(QFrame.Plain)

        self.gridLayout.addWidget(self_dummy, 6, 1, 1, 1)

        self_dummy_2 = QFrame(self.group_settings_general)
        self_dummy_2.setObjectName("frame_settings_dummy_2")
        self_dummy_2.setFrameShape(QFrame.NoFrame)
        self_dummy_2.setFrameShadow(QFrame.Plain)

        self.gridLayout.addWidget(self_dummy_2, 2, 3, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)

        self_footer = QFrame(self.group_settings_general)
        self_footer.setObjectName("frame_settings_footer")
        self_footer.setMaximumSize(QSize(16777215, 40))
        self_footer.setFrameShape(QFrame.NoFrame)
        self_footer.setFrameShadow(QFrame.Plain)
        self.horizontalLayout_3 = QHBoxLayout(self_footer)
        self.horizontalLayout_3.setSpacing(6)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 6, 0)
        self.frame_2 = QFrame(self_footer)
        self.frame_2.setObjectName("frame_2")
        self.frame_2.setStyleSheet("")
        self.frame_2.setFrameShape(QFrame.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Plain)

        self.horizontalLayout_3.addWidget(self.frame_2)

        self.btn_apply_settings = QPushButton(self_footer)
        self.btn_apply_settings.setObjectName("btn_apply_settings")
        self.btn_apply_settings.setMinimumSize(QSize(0, 24))
        self.btn_apply_settings.setMaximumSize(QSize(100, 24))
        self.btn_apply_settings.setFont(font)
        self.btn_apply_settings.setFocusPolicy(Qt.NoFocus)

        self.horizontalLayout_3.addWidget(self.btn_apply_settings)

        self.btn_reset_settings = QPushButton(self_footer)
        self.btn_reset_settings.setObjectName("btn_reset_settings")
        self.btn_reset_settings.setMinimumSize(QSize(0, 24))
        self.btn_reset_settings.setMaximumSize(QSize(100, 24))
        self.btn_reset_settings.setFont(font)
        self.btn_reset_settings.setFocusPolicy(Qt.NoFocus)

        self.horizontalLayout_3.addWidget(self.btn_reset_settings)

        self.verticalLayout_2.addWidget(self_footer)
        self.verticalLayout.addWidget(self.group_settings_general)
        self.btn_browse_proxy.setIcon(
            QIcon(os.path.dirname(os.path.dirname(__file__)) + '/icons/explore.png')
        )
        self.btn_browse_ffmpeg.setIcon(
            QIcon(os.path.dirname(os.path.dirname(__file__)) + '/icons/explore.png')
        )
        self.btn_browse_proxy.setStyleSheet('QPushButton{background-color: #313131;}')
        self.btn_browse_ffmpeg.setStyleSheet('QPushButton{background-color: #313131;}')

        QMetaObject.connectSlotsByName(self)
        self.setWindowTitle(QCoreApplication.translate("Settings", "Form", None))
        self.group_settings_general.setTitle(QCoreApplication.translate("Settings", "General", None))
        self.threadsLabel.setText(QCoreApplication.translate("Settings", "No. of Threads", None))
        self.always_on_top_label.setText(QCoreApplication.translate("Settings", "Always on top", None))
        self.proxyLabel.setText(QCoreApplication.translate("Settings", "Proxy", None))
        self.jsonLabel.setText(QCoreApplication.translate("Settings", "Json", None))
        self.btn_apply_settings.setText(QCoreApplication.translate("Settings", "Apply", None))
        self.btn_reset_settings.setText(QCoreApplication.translate("Settings", "Reset", None))

