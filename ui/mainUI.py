"""
Main User Interface Module
=========================

This module provides the main user interface for the application, combining various UI components
such as categories, actions, thumbnails, settings, and a status bar. It is responsible for
organizing and managing the layout and interactions between these components.

Key Components:
    - **Categories**: Manages grouping and categorization of items.
    - **ActionsUI**: Provides action buttons (e.g., settings, filters).
    - **ThumbnailUI**: Displays thumbnails for items.
    - **SettingsUI**: Handles application settings.
    - **StatusBar**: Displays status information.

Usage:
    - Use the `setupUi` method to initialize and set up the main UI.
    - Connect signals to handle user interactions and updates across components.
"""

# -------------------------------- built-in Modules ----------------------------------
from typing import Optional

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets, QtCore
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore

# -------------------------------- Custom Modules ------------------------------------
from ui import _categoriesUI, _settingsUI, _actionsUI, _thumbnailUI, _stausbarUI


class MainUI:
    """
    Main user interface class for organizing and managing UI components.

    This class sets up the layout and connections between categories, actions, thumbnails,
    settings, and the status bar.

    :param mainWidget: The main widget where the UI will be set up.
    :type mainWidget: QWidget
    """
    def setupUi(self, mainWidget: QtWidgets.QWidget):
        """
        Set up the main user interface.

        :param mainWidget: The main widget to set up the UI in.
        :type mainWidget: QWidget
        """
        if not mainWidget.objectName():
            mainWidget.setObjectName("Ulaavi")
            mainWidget.setWindowTitle('Ulaavi-2.0.0')

        self.categories = _categoriesUI.Categories()
        self.actions_ui = _actionsUI.ActionsUI()
        self.thumbnail = _thumbnailUI.ThumbnailUI()
        self.settings = _settingsUI.SettingsUI()
        self.status = _stausbarUI.StatusBar()

        self.__hLayoutMain = QtWidgets.QHBoxLayout(mainWidget)
        self.__hLayoutMain.setContentsMargins(0, 0, 0, 0)

        self.__frame_main = QtWidgets.QFrame()
        self.__vLayoutMain = QtWidgets.QVBoxLayout(self.__frame_main)

        self.__splitter = QtWidgets.QSplitter()
        self.__splitter.setObjectName("splitter")
        self.__splitter.setOrientation(QtCore.Qt.Horizontal)

        self.__leftFrame = QtWidgets.QFrame(self.__splitter)
        self.__rightFrame = QtWidgets.QFrame(self.__splitter)

        self.__hLayout = QtWidgets.QHBoxLayout(self.__leftFrame)
        self.__vLayout = QtWidgets.QVBoxLayout(self.__rightFrame)

        self.__vLayout.addWidget(self.actions_ui)
        self.__vLayout.addWidget(self.thumbnail)
        self.__hLayout.addWidget(self.categories)

        self.__leftFrame.setFocusPolicy(QtCore.Qt.NoFocus)
        self.__leftFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.__leftFrame.setFrameShadow(QtWidgets.QFrame.Plain)

        self.__rightFrame.setFocusPolicy(QtCore.Qt.NoFocus)
        self.__rightFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.__rightFrame.setFrameShadow(QtWidgets.QFrame.Plain)

        self.__vLayoutMain.addWidget(self.__splitter)
        self.__vLayoutMain.addWidget(self.status)

        self.__vLayoutMain.setContentsMargins(0, 0, 0, 0)
        self.__hLayout.setContentsMargins(0, 0, 0, 0)
        self.__vLayout.setContentsMargins(0, 0, 0, 0)
        self.__splitter.setContentsMargins(0, 0, 0, 0)
        self.__leftFrame.setMaximumWidth(350)

        self.__hLayoutMain.addWidget(self.__frame_main)
        self.__hLayoutMain.addWidget(self.settings)

        self._set_widget_connections()

    def _set_widget_connections(self) -> None:
        """
        Set up signal connections between UI components.
        This method connects signals from actions, categories, and settings to their respective slots.
        """
        self.actions_ui.on_settings.connect(self._toggle_settings_widget)
        self.settings.on_close.connect(self.__frame_main.show)

        self.categories.tree.on_create.connect(self._update_group_attributes)
        self.categories.tree.on_change.connect(self._update_group_attributes)
        self.categories.tree.on_rename.connect(self._update_on_rename_category)

        self.categories.group.on_group_change.connect(self._on_change_group)
        self.categories.group.on_group_new.connect(self._on_change_group)
        self.categories.group.on_group_remove.connect(self._update_on_group_remove)

        self.actions_ui.filters.on_tags_filter_changed.connect(self.thumbnail.reset_attributes)
        self.thumbnail.on_delete_proxy.connect(self.thumbnail.reset_attributes)

    def _toggle_settings_widget(self) -> None:
        """
        Toggle the visibility of the settings widget.
        This method hides the main frame and shows the settings widget.
        """
        self.settings.toggle_widget_visibility()
        self.__frame_main.hide()

    def _update_group_attributes(self, group: str, category: str) -> None:
        """
        Update group and category attributes in the thumbnail UI.

        :param group: The name of the group.
        :type group: str
        :param category: The name of the category.
        :type category: str
        """
        self.thumbnail.current_group = group
        self.thumbnail.current_category = category if category != "root" else None
        self.thumbnail.reset_attributes()

    def _update_on_rename_category(self, group: str, old_category: str, new_category: str) -> None:
        """
        Update the current category when a category is renamed.

        :param group: The name of the group.
        :type group: str
        :param old_category: The old name of the category.
        :type old_category: str
        :param new_category: The new name of the category.
        :type new_category: str
        """
        self.thumbnail.current_group = group
        self.thumbnail.current_category = new_category

    def _update_on_group_remove(self, group: str) -> None:
        """
        Update the current group when a group is removed.

        :param group: The name of the removed group.
        :type group: str
        """
        self.categories.tree.current_group = self.categories.group.current_group
        self.thumbnail.current_group = self.categories.group.current_group

    def _on_change_group(self, group: Optional[str]) -> None:
        """
        Handle changes to the current group.

        :param group: The name of the current group.
        :type group: str or None
        """
        if not group:
            self.categories.tree.setEnabled(False)
        else:
            self.categories.tree.setEnabled(True)
        self.categories.tree.root_item()

        self.categories.tree.current_group = group
        self.thumbnail.current_group = group
        self.thumbnail.reset_attributes()
