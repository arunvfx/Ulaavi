# -*- coding: utf-8 -*-

from PySide2.QtWidgets import QWidget, QVBoxLayout, QFrame, QHBoxLayout, QLabel, QFormLayout, QComboBox, QLineEdit, \
    QPushButton
from PySide2.QtCore import QSize, Qt, QCoreApplication


class Ui_Add_Script(QWidget):
    def __init__(self):
        super(Ui_Add_Script, self).__init__()
        self.resize(600, 300)
        self.setMinimumSize(QSize(600, 300))
        self.setMaximumSize(QSize(600, 300))
        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, -1, 0)
        self.frame = QFrame(self)
        self.frame.setObjectName("frame")
        self.frame.setMaximumSize(QSize(16777215, 260))
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Plain)
        self.horizontalLayout = QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame_thumb = QFrame(self.frame)
        self.frame_thumb.setObjectName("frame_thumb")
        self.frame_thumb.setMinimumSize(QSize(250, 0))
        self.frame_thumb.setMaximumSize(QSize(250, 180))
        self.frame_thumb.setFrameShape(QFrame.NoFrame)
        self.frame_thumb.setFrameShadow(QFrame.Plain)
        self.horizontalLayout_2 = QHBoxLayout(self.frame_thumb)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_thumb = QLabel(self.frame_thumb)
        self.label_thumb.setObjectName("label_thumb")

        self.horizontalLayout_2.addWidget(self.label_thumb)

        self.horizontalLayout.addWidget(self.frame_thumb)

        self.frame_category = QFrame(self.frame)
        self.frame_category.setObjectName("frame_category")
        self.frame_category.setFrameShape(QFrame.NoFrame)
        self.frame_category.setFrameShadow(QFrame.Plain)
        self.formLayout = QFormLayout(self.frame_category)
        self.formLayout.setObjectName("formLayout")
        self.label_group = QLabel(self.frame_category)
        self.label_group.setObjectName("label_group")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_group)

        self.comboBox_group = QComboBox(self.frame_category)
        self.comboBox_group.setObjectName("comboBox_group")
        self.comboBox_group.setMaximumSize(QSize(16777215, 25))
        self.comboBox_group.setMinimumSize(QSize(260, 25))

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.comboBox_group)

        self.label_category = QLabel(self.frame_category)
        self.label_category.setObjectName("label_category")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_category)

        self.comboBox_category = QComboBox(self.frame_category)
        self.comboBox_category.setObjectName("comboBox_category")
        self.comboBox_category.setMaximumSize(QSize(16777215, 25))
        self.comboBox_category.setMinimumSize(QSize(260, 25))

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.comboBox_category)

        self.label_sub_category = QLabel(self.frame_category)
        self.label_sub_category.setObjectName("label_sub_category")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_sub_category)

        self.comboBox_sub_category = QComboBox(self.frame_category)
        self.comboBox_sub_category.setObjectName("comboBox_sub_category")
        self.comboBox_sub_category.setMaximumSize(QSize(16777215, 25))
        self.comboBox_sub_category.setMinimumSize(QSize(260, 25))

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.comboBox_sub_category)

        self.label_label = QLabel(self.frame_category)
        self.label_label.setObjectName("label_label")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_label)

        self.lineEdit_label = QLineEdit(self.frame_category)
        self.lineEdit_label.setObjectName("lineEdit_label")
        self.lineEdit_label.setMaximumSize(QSize(16777215, 25))
        self.lineEdit_label.setMinimumSize(QSize(240, 25))

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.lineEdit_label)

        self.label_info = QLabel(self.frame_category)
        self.label_info.setObjectName("label_info")

        self.formLayout.setWidget(4, QFormLayout.FieldRole, self.label_info)

        self.horizontalLayout.addWidget(self.frame_category)

        self.verticalLayout.addWidget(self.frame)

        self.frame_2 = QFrame(self)
        self.frame_2.setObjectName("frame_2")
        self.frame_2.setMinimumSize(QSize(0, 34))
        self.frame_2.setMaximumSize(QSize(16777215, 34))
        self.frame_2.setFrameShape(QFrame.NoFrame)
        self.frame_2.setFrameShadow(QFrame.Plain)
        self.horizontalLayout_3 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, -1, 0)
        self.label_7 = QLabel(self.frame_2)
        self.label_7.setObjectName("label_7")

        self.horizontalLayout_3.addWidget(self.label_7)

        self.add_btn = QPushButton(self.frame_2)
        self.add_btn.setObjectName("add_btn")
        self.add_btn.setMinimumSize(QSize(0, 24))
        self.add_btn.setMaximumSize(QSize(120, 24))
        self.add_btn.setFocusPolicy(Qt.NoFocus)

        self.horizontalLayout_3.addWidget(self.add_btn)

        self.cancel_btn = QPushButton(self.frame_2)
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.setMinimumSize(QSize(0, 24))
        self.cancel_btn.setMaximumSize(QSize(120, 24))
        self.cancel_btn.setFocusPolicy(Qt.NoFocus)

        self.horizontalLayout_3.addWidget(self.cancel_btn)
        self.verticalLayout.addWidget(self.frame_2)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)

        self.setWindowTitle(QCoreApplication.translate("Add_Script", "Add Templete", None))
        self.label_group.setText(QCoreApplication.translate("Add_Script", "Group", None))
        self.label_category.setText(QCoreApplication.translate("Add_Script", "Category", None))
        self.label_sub_category.setText(QCoreApplication.translate("Add_Script", "Sub-Category", None))
        self.label_label.setText(QCoreApplication.translate("Add_Script", "Label", None))
        self.add_btn.setText(QCoreApplication.translate("Add_Script", "Add", None))
        self.cancel_btn.setText(QCoreApplication.translate("Add_Script", "Cancel", None))

