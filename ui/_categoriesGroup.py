"""
The CategoriesGroup module provides a custom Qt widget for managing category groups in a user interface.
 It allows users to add, remove, and switch between groups using a combo box and buttons. The widget emits signals
 when a group is added, removed, or changed, enabling integration with other parts of the application.
"""

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
    A custom Qt widget for managing category groups.

    This widget provides functionality to add, remove, and switch between category groups.
    It consists of a combo box to display groups, and buttons to add or remove groups.
    Signals are emitted when a group is added, removed, or changed.

    :signal on_group_new: Emitted when a new group is added. The signal carries the new group name (str).
    :signal on_group_change: Emitted when the selected group changes. The signal carries the current group name (str).
    :signal on_group_remove: Emitted when a group is removed. The signal carries the removed group name (str).
    """
    on_group_new = QtCore.Signal(str)
    on_group_change = QtCore.Signal(str)
    on_group_remove = QtCore.Signal(str)

    def __init__(self) -> None:
        """
        Initializes the CategoriesGroup widget.

        Sets up the layout, widgets, and connections.
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
        """
        Configures the properties of the widgets.

        Sets text, size, and layout properties for the combo box and buttons.
        """
        self.btn_add.setText('+')
        self.btn_remove.setText('-')
        self.btn_add.setFixedSize(25, 25)
        self.btn_remove.setFixedSize(25, 25)
        self.cmb_group.setMinimumHeight(25)
        self.cmb_group.setMaximumHeight(25)

        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.setSpacing(1)

    def _widget_connections(self):
        """
        Connects widget signals to their respective slots.

        Sets up connections for the add, remove, and group change actions.
        """
        self.btn_add.clicked.connect(self._create_new_group)
        self.btn_remove.clicked.connect(self._remove_group)
        self.cmb_group.currentIndexChanged.connect(
            lambda: self.on_group_change.emit(self.current_group))

    def _create_new_group(self):
        """
        Creates a new category group.

        Prompts the user to enter a group name using an input dialog.
        If the user confirms, the new group is added to the combo box and the `on_group_new` signal is emitted.
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
        """
        Removes the currently selected group.

        Prompts the user to confirm the removal using a popup message.
        If confirmed, the group is removed from the combo box and the `on_group_remove` signal is emitted.
        """
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
        Gets the currently selected group name.

        :return: The name of the currently selected group.
        :rtype: str
        """
        return self.cmb_group.currentText()

    def add_groups(self, groups: tuple) -> None:
        """
        Adds multiple groups to the combo box.

        Clears the existing groups and adds the provided groups in sorted order.

        :param groups: A tuple of group names to add.
        :type groups: tuple
        """
        self.cmb_group.clear()
        self.cmb_group.addItems(sorted(groups))
