"""
UI Components for Actions and Filters
====================================

This module provides custom Qt widgets for managing actions (e.g., snap script) and filters (e.g., tags, search).
It is designed to be reusable and modular, with clear separation of concerns between actions and filters.

Key Classes:
    - **ActionsUI**: A container widget that combines `Actions` and `Filters` widgets with a settings button.
    - **Actions**: A widget for action buttons (e.g., snap script).
    - **Filters**: A widget for filtering options (e.g., tags dropdown, search bar).

Key Features:
    - **Reusable Components**: Modular design for easy integration into larger applications.
    - **Custom Signals**: Emit signals for user interactions like button clicks and filter changes.
    - **Dynamic Updates**: Supports dynamic updates for tags and search functionality.
    - **Settings Integration**: Includes a settings button for additional configuration.

Usage:
    - Use `ActionsUI` to create a combined interface for actions and filters.
    - Connect signals like `on_snap_script`, `on_tags_filter_changed`, and `on_settings` to handle user interactions.
    - Add tags dynamically using the `add_tags` method in the `Filters` class.

Dependencies:
    - PySide2 or PySide6 for Qt bindings.
    - `pathlib.Path` for resolving file paths.
"""

# -------------------------------- built-in Modules ----------------------------------
from pathlib import Path
from typing import List

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore, QtGui


# -------------------------------- Custom Modules ------------------------------------


class ActionsUI(QtWidgets.QWidget):
    """
    A container widget that combines `Actions` and `Filters` widgets with a settings button.
    This widget provides a unified interface for actions (e.g., snap script) and filters (e.g., tags, search),
    along with a settings button for additional configuration.

    :param parent: The parent widget, defaults to None.
    :type parent: QWidget, optional

    Signals:
    --------
    on_settings : Signal()
        Emitted when the settings button is clicked.
    """

    on_settings = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.__hLayout = QtWidgets.QHBoxLayout(self)
        self.actions = Actions(self)
        self.filters = Filters(self)

        self.btn_settings = QtWidgets.QPushButton()

        self.__hLayout.addWidget(self.actions)
        self.__hLayout.addWidget(self.filters)
        self.__hLayout.addWidget(self.btn_settings)

        self._set_widget_properties()
        self._set_widget_connections()

    def _set_widget_properties(self) -> None:
        """
        Connect signals to their respective slots.
        This method sets up the signal-slot connections for the settings button.
        """

        self.btn_settings.setFixedHeight(26)
        self.btn_settings.setFlat(True)
        self.btn_settings.setFixedSize(QtCore.QSize(26, 26))
        self.btn_settings.setIcon(QtGui.QIcon(f'{Path(__file__).parent.parent}/icons/setting.png'))

    def _set_widget_connections(self):
        self.btn_settings.clicked.connect(lambda: self.on_settings.emit())


class Actions(QtWidgets.QFrame):
    """
    A widget for action buttons (e.g., snap script).
    This widget provides buttons for performing actions such as triggering a snap script.
    It is designed to be lightweight and reusable.

    :param parent: The parent widget, defaults to None.
    :type parent: QWidget, optional

    Signals:
    --------
    on_snap_script : Signal()
        Emitted when the snap script button is clicked.

    on_refresh : Signal()
        Emitted when the refresh button is clicked (currently unused).
    """
    on_snap_script = QtCore.Signal()
    on_refresh = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.btn_snap_script = QtWidgets.QPushButton()
        # self.btn_refresh = QtWidgets.QPushButton()

        self.__hLayout = QtWidgets.QHBoxLayout(self)
        self.__hLayout.addWidget(self.btn_snap_script)
        # self.__hLayout.addWidget(self.btn_refresh)

        self._set_widget_properties()

    def _set_widget_properties(self) -> None:
        """
        Set properties for the action buttons and frame.
        This method configures the appearance and behavior of the buttons and the frame.
        """
        # self.btn_refresh.setFlat(True)
        self.btn_snap_script.setFlat(True)
        # self.btn_refresh.setFixedSize(QtCore.QSize(26, 26))
        self.btn_snap_script.setFixedSize(QtCore.QSize(26, 26))
        # self.btn_refresh.setIcon(QtGui.QIcon(f'{Path(__file__).parent.parent}/icons/refresh.png'))
        self.btn_snap_script.setIcon(QtGui.QIcon(f'{Path(__file__).parent.parent}/icons/capture.png'))
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setFrameShadow(QtWidgets.QFrame.Plain)
        self.__hLayout.setContentsMargins(0, 0, 0, 0)


class Filters(QtWidgets.QFrame):
    """
    A widget for filtering options (e.g., tags dropdown, search bar).

    :param parent: The parent widget, defaults to None.
    :type parent: QWidget, optional

    Signals:
    --------
    on_tags_filter_changed : Signal(str, str)
        Emitted when the selected tag or search text changes.
        - **Parameters**:
            - `tag` (str): The currently selected tag from the dropdown.
            - `search_text` (str): The current text in the search bar.

    on_change_search_text : Signal(str, str)
        Emitted when the search text changes.
        - **Parameters**:
            - `tag` (str): The currently selected tag from the dropdown.
            - `search_text` (str): The current text in the search bar.
    """
    on_tags_filter_changed = QtCore.Signal(str, str)
    on_change_search_text = QtCore.Signal(str, str)

    def __init__(self, parent=None):
        """
        Initialize attributes
        """
        super().__init__(parent)

        self.lbl_tags = QtWidgets.QLabel('\tTags')
        self.cmb_tags = QtWidgets.QComboBox()

        self.lineEdit_search = QtWidgets.QLineEdit()
        self.lineEdit_search.setPlaceholderText('Search here...')

        self.__hLayout = QtWidgets.QHBoxLayout(self)
        self.__hLayout.addWidget(self.lbl_tags)
        self.__hLayout.addWidget(self.cmb_tags)
        self.__hLayout.addWidget(self.lineEdit_search)

        self._set_widget_properties()
        self._Set_widget_connections()

    @property
    def current_tag(self) -> str:
        """
        Get the currently selected tag from the dropdown.

        :return: The selected tag or an empty string if no tag is selected.
        :rtype: str
        """
        tag = self.cmb_tags.currentText()
        return tag if tag.strip() != '-' else ''

    @property
    def search_text(self):
        """
        Get the current search text from the search bar.

        :return: The search text.
        :rtype: str
        """
        return self.lineEdit_search.text()

    def _set_widget_properties(self) -> None:
        """Set properties for the filter widgets."""
        self.cmb_tags.setFixedHeight(26)
        self.lineEdit_search.setFixedHeight(26)
        self.lineEdit_search.setFrame(QtWidgets.QFrame.NoFrame)

    def _Set_widget_connections(self) -> None:
        """
        Connect signals to their respective slots.
        """
        self.cmb_tags.currentIndexChanged.connect(self._on_change_current_index)
        self.lineEdit_search.textChanged.connect(self._on_change_current_index)

    def _on_change_current_index(self) -> None:
        """
        Emit signals when the tag or search text changes.
        """
        self.on_tags_filter_changed.emit(self.current_tag, self.lineEdit_search.text().strip())

    def add_tags(self, tags: List[str]) -> None:
        """
        Add tags to the dropdown menu.

        :param tags: A list of tags to add.
        :type tags: list
        """
        self.cmb_tags.clear()
        tags.insert(0, '-'.center(10, ' '))
        self.cmb_tags.addItems(tags)
