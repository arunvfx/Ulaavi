try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *

except ModuleNotFoundError:
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *


class PreferencesGroup:
    def setupUi(self, Preferences):
        if not Preferences.objectName():
            Preferences.setObjectName(u"Preferences")
        Preferences.resize(586, 216)
        self.verticalLayout = QVBoxLayout(Preferences)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_preferences = QGroupBox(Preferences)
        self.groupBox_preferences.setObjectName(u"groupBox_preferences")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox_preferences)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.frame_preferences = QFrame(self.groupBox_preferences)
        self.frame_preferences.setObjectName(u"frame_preferences")
        self.frame_preferences.setFrameShape(QFrame.NoFrame)
        self.frame_preferences.setFrameShadow(QFrame.Plain)
        self.horizontalLayout = QHBoxLayout(self.frame_preferences)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setHorizontalSpacing(6)
        self.gridLayout.setVerticalSpacing(9)
        self.gridLayout.setContentsMargins(10, -1, -1, -1)
        self.lineEdit_proxy = QLineEdit(self.frame_preferences)
        self.lineEdit_proxy.setObjectName(u"lineEdit_proxy")
        self.lineEdit_proxy.setMinimumSize(QSize(400, 0))
        self.lineEdit_proxy.setFocusPolicy(Qt.ClickFocus)

        self.gridLayout.addWidget(self.lineEdit_proxy, 0, 1, 1, 1)

        self.lineEdit_json = QLineEdit(self.frame_preferences)
        self.lineEdit_json.setObjectName(u"lineEdit_json")
        self.lineEdit_json.setFocusPolicy(Qt.ClickFocus)

        self.gridLayout.addWidget(self.lineEdit_json, 1, 1, 1, 1)

        self.btn_browse_json = QPushButton(self.frame_preferences)
        self.btn_browse_json.setObjectName(u"btn_browse_json")
        self.btn_browse_json.setMinimumSize(QSize(24, 24))
        self.btn_browse_json.setMaximumSize(QSize(24, 24))

        self.gridLayout.addWidget(self.btn_browse_json, 1, 2, 1, 1)

        self.label_resolution = QLabel(self.frame_preferences)
        self.label_resolution.setObjectName(u"label_resolution")
        self.label_resolution.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_resolution, 2, 0, 1, 1)

        self.label_json = QLabel(self.frame_preferences)
        self.label_json.setObjectName(u"label_json")
        self.label_json.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_json, 1, 0, 1, 1)

        self.label_proxy = QLabel(self.frame_preferences)
        self.label_proxy.setObjectName(u"label_proxy")
        self.label_proxy.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_proxy, 0, 0, 1, 1)

        self.btn_browse_proxy = QPushButton(self.frame_preferences)
        self.btn_browse_proxy.setObjectName(u"btn_browse_proxy")
        self.btn_browse_proxy.setMinimumSize(QSize(24, 24))
        self.btn_browse_proxy.setMaximumSize(QSize(24, 24))

        self.gridLayout.addWidget(self.btn_browse_proxy, 0, 2, 1, 1)

        self.label_scale = QLabel(self.frame_preferences)
        self.label_scale.setObjectName(u"label_scale")
        self.label_scale.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_scale, 4, 0, 1, 1)

        self.label_thread_count = QLabel(self.frame_preferences)
        self.label_thread_count.setObjectName(u"label_thread_count")
        self.label_thread_count.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.gridLayout.addWidget(self.label_thread_count, 3, 0, 1, 1)

        self.slider_thumbnail_scale = QSlider(self.frame_preferences)
        self.slider_thumbnail_scale.setObjectName(u"slider_thumbnail_scale")
        self.slider_thumbnail_scale.setMinimum(1)
        self.slider_thumbnail_scale.setMaximum(5)
        self.slider_thumbnail_scale.setOrientation(Qt.Horizontal)

        self.gridLayout.addWidget(self.slider_thumbnail_scale, 4, 1, 1, 1)

        self.lineEdit_thread_count = QLineEdit(self.frame_preferences)
        self.lineEdit_thread_count.setObjectName(u"lineEdit_thread_count")
        self.lineEdit_thread_count.setMinimumSize(QSize(100, 0))
        self.lineEdit_thread_count.setMaximumSize(QSize(100, 16777215))
        self.lineEdit_thread_count.setFocusPolicy(Qt.ClickFocus)

        self.gridLayout.addWidget(self.lineEdit_thread_count, 3, 1, 1, 1)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.lineEdit_res_width = QLineEdit(self.frame_preferences)
        self.lineEdit_res_width.setObjectName(u"lineEdit_res_width")
        self.lineEdit_res_width.setMinimumSize(QSize(50, 0))
        self.lineEdit_res_width.setMaximumSize(QSize(100, 16777215))
        self.lineEdit_res_width.setFocusPolicy(Qt.ClickFocus)

        self.horizontalLayout_5.addWidget(self.lineEdit_res_width)

        self.horizontalSpacer_4 = QSpacerItem(10, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_4)

        self.lineEdit_res_height = QLineEdit(self.frame_preferences)
        self.lineEdit_res_height.setObjectName(u"lineEdit_res_height")
        self.lineEdit_res_height.setMinimumSize(QSize(50, 0))
        self.lineEdit_res_height.setMaximumSize(QSize(100, 16777215))
        self.lineEdit_res_height.setFocusPolicy(Qt.ClickFocus)

        self.horizontalLayout_5.addWidget(self.lineEdit_res_height)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_5.addItem(self.horizontalSpacer_3)

        self.gridLayout.addLayout(self.horizontalLayout_5, 2, 1, 1, 1)

        self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_5, 1, 3, 1, 1)

        self.horizontalLayout.addLayout(self.gridLayout)

        self.verticalLayout_2.addWidget(self.frame_preferences)

        self.frame_pref_actions = QFrame(self.groupBox_preferences)
        self.frame_pref_actions.setObjectName(u"frame_pref_actions")
        self.frame_pref_actions.setMinimumSize(QSize(0, 30))
        self.frame_pref_actions.setMaximumSize(QSize(16777215, 30))
        self.frame_pref_actions.setFrameShape(QFrame.NoFrame)
        self.frame_pref_actions.setFrameShadow(QFrame.Plain)
        self.horizontalLayout_4 = QHBoxLayout(self.frame_pref_actions)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_preferences = QHBoxLayout()
        self.horizontalLayout_preferences.setObjectName(u"horizontalLayout_preferences")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_preferences.addItem(self.horizontalSpacer)

        self.btn_apply = QPushButton(self.frame_pref_actions)
        self.btn_apply.setObjectName(u"btn_apply")
        self.btn_apply.setMinimumSize(QSize(0, 24))
        self.btn_apply.setMaximumSize(QSize(16777215, 24))

        self.horizontalLayout_preferences.addWidget(self.btn_apply)

        self.btn_reset = QPushButton(self.frame_pref_actions)
        self.btn_reset.setObjectName(u"btn_reset")
        self.btn_reset.setMinimumSize(QSize(0, 24))
        self.btn_reset.setMaximumSize(QSize(16777215, 24))

        self.horizontalLayout_preferences.addWidget(self.btn_reset)

        self.btn_close = QPushButton(self.frame_pref_actions)
        self.btn_close.setObjectName(u"btn_close")
        self.btn_close.setMinimumSize(QSize(0, 24))
        self.btn_close.setMaximumSize(QSize(16777215, 24))

        self.horizontalLayout_preferences.addWidget(self.btn_close)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_preferences.addItem(self.horizontalSpacer_2)

        self.horizontalLayout_4.addLayout(self.horizontalLayout_preferences)

        self.verticalLayout_2.addWidget(self.frame_pref_actions)

        self.verticalLayout.addWidget(self.groupBox_preferences)

        self.retranslateUi(Preferences)

        QMetaObject.connectSlotsByName(Preferences)
        # setupUi

    def retranslateUi(self, Preferences):
        Preferences.setWindowTitle(QCoreApplication.translate("Preferences", u"Form", None))
        self.groupBox_preferences.setTitle(QCoreApplication.translate("Preferences", u"Preferences", None))
        self.btn_browse_json.setText("")
        self.label_resolution.setText(QCoreApplication.translate("Preferences", u"Proxy Resolution", None))
        self.label_json.setText(QCoreApplication.translate("Preferences", u"Json", None))
        self.label_proxy.setText(QCoreApplication.translate("Preferences", u"Proxy", None))
        self.btn_browse_proxy.setText("")
        self.label_scale.setText(QCoreApplication.translate("Preferences", u"Thumbnail Scale", None))
        self.label_thread_count.setText(QCoreApplication.translate("Preferences", u"Thread Count", None))
        self.btn_apply.setText(QCoreApplication.translate("Preferences", u"Apply", None))
        self.btn_reset.setText(QCoreApplication.translate("Preferences", u"Reset", None))
        self.btn_close.setText(QCoreApplication.translate("Preferences", u"Close", None))