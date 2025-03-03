import sys

from PySide2 import QtWidgets, QtCore
from . import commonWidgets


class CategoriesGroup(QtWidgets.QFrame):
    """
    categories group
    """
    new_group = QtCore.Signal(str)
    group_change_event = QtCore.Signal(str)
    remove_group = QtCore.Signal(str)

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
        self.btn_add.clicked.connect(self._add_new_group)
        self.btn_remove.clicked.connect(self._remove_group)
        self.cmb_group.currentIndexChanged.connect(self._group_change_event)

    def _add_new_group(self):
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

            self.new_group.emit(group_name)

    def _remove_group(self):
        remove_group: bool = commonWidgets.popup_message(
            'Remove Group',
            f'Are you sure wanna remove the group: {self.current_group} ? ',
            msgType='question',
            parent=self)

        if remove_group:
            current_group = self.current_group
            self.cmb_group.removeItem(self.cmb_group.currentIndex())
            self.remove_group.emit(current_group)

    def _group_change_event(self):
        self.group_change_event.emit(self.current_group)

    @property
    def current_group(self) -> str:
        """
        currne
        :return:
        """
        return self.cmb_group.currentText()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    p = CategoriesGroup()
    p.show()

    sys.exit(app.exec_())
