# -------------------------------- built-in Modules ----------------------------------

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets, QtCore
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore

# -------------------------------- Custom Modules ------------------------------------
from . import commonWidgets


class CategoriesGroup(QtWidgets.QFrame):
    """
    categories group
    """
    on_group_new = QtCore.Signal(str)
    on_group_change = QtCore.Signal(str)
    on_group_remove = QtCore.Signal(str)

    def __init__(self) -> None:
        """
        initialize variables
        """
        super().__init__()
        self.__layout = QtWidgets.QHBoxLayout(self)
        self.cmb_group = QtWidgets.QComboBox()
        self.btn_add = QtWidgets.QPushButton()
        self.btn_remove = QtWidgets.QPushButton()

        self.__layout.addWidget(self.cmb_group)
        self.__layout.addWidget(self.btn_add)
        self.__layout.addWidget(self.btn_remove)

        self.setLayout(self.__layout)

        self._set_widget_properties()
        self._widget_connections()

    def _set_widget_properties(self) -> None:
        self.btn_add.setText('+')
        self.btn_remove.setText('-')
        self.btn_add.setFixedSize(25, 25)
        self.btn_remove.setFixedSize(25, 25)
        self.cmb_group.setMinimumHeight(25)
        self.cmb_group.setMaximumHeight(25)

        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.setSpacing(1)

    def _widget_connections(self):

        self.btn_add.clicked.connect(self._create_new_group)
        self.btn_remove.clicked.connect(self._remove_group)
        self.cmb_group.currentIndexChanged.connect(
            lambda: self.on_group_change.emit(self.current_group))

    def _create_new_group(self):
        """
        add category group
        :return:
        """
        group_name, btn_pressed = commonWidgets.get_input_widget(
            'Group Name',
            'Enter the Group Name',
            self)

        if btn_pressed:
            self.cmb_group.addItem(group_name)
            self.cmb_group.setCurrentText(group_name)
            self.on_group_new.emit(group_name)

    def _remove_group(self):
        remove_group: bool = commonWidgets.popup_message(
            'Remove Group',
            f'Are you sure wanna remove the group: {self.current_group} ? ',
            msgType='question',
            parent=self)

        if remove_group:
            current_group = self.current_group
            self.cmb_group.removeItem(self.cmb_group.currentIndex())
            self.on_group_remove.emit(current_group)

    @property
    def current_group(self) -> str:
        """
        get current group
        :return: group name
        :rtype: str
        """
        return self.cmb_group.currentText()

    def add_groups(self, groups) -> None:
        """
        add groups to QComboBox.

        :param groups: list of groups
        :type groups: list
        :return: None
        :rtype: None
        """
        self.cmb_group.clear()
        for group in groups:
            self.cmb_group.addItem(group)
