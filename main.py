"""
Ulaavi Module
=============

This module provides the main application window for the Ulaavi tool, which is used to display and manage thumbnails.
It integrates the UI components with backend operations for handling file management, thumbnail generation, and user interactions.

Key Features:
    - **UI Integration**: Connects the UI components with backend operations using signals and slots.
    - **Thumbnail Management**: Handles thumbnail display, scaling, and updates.
    - **File Operations**: Supports file drop events, proxy file creation, and deletion.
    - **Tag Management**: Allows creating, adding, and removing tags from files.
    - **Dynamic Updates**: Automatically updates the UI based on backend operations.

Classes:
    - **Ulaavi**: The main application window that integrates the UI and backend operations.

Dependencies:
    - **PySide2/PySide6**: For Qt-based GUI components.
    - **ui.mainUI**: The main UI layout and components.
    - **_operations**: The backend operations for handling file and thumbnail management.
"""

# -------------------------------- built-in Modules ----------------------------------
import sys

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets, QtCore
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore

# -------------------------------- Custom Modules ------------------------------------
from ui import mainUI
import _operations


class Ulaavi(QtWidgets.QWidget, mainUI.MainUI):
    """
    The main application window for the Ulaavi tool.

    This class integrates the UI components with backend operations to provide a seamless user experience.
    It handles thumbnail display, file management, and user interactions. The class inherits from
    `QtWidgets.QWidget` and `mainUI.MainUI` to combine the functionality of a Qt widget with the custom UI layout.

    :ivar __ops: An instance of `_operations.Operations` for managing backend operations.
                  This object handles core functionalities like file handling, thumbnail generation, and tag management.

    Notes:
        - The class relies on the `_operations.Operations` class for backend logic and the `mainUI.MainUI` class for UI layout.
        - Ensure that the required dependencies (e.g., PySide2 or PySide6) are installed before using this class.
    """

    def __init__(self):
        """Initialize the Ulaavi application window."""
        super().__init__()
        self.setupUi(self)
        self.resize(1400, 700)

        self.__ops = _operations.Operations()
        self._widget_connections()
        self.execute_on_startup()

    def _widget_connections(self) -> None:
        """
        Connect UI signals to backend operations.

        This method sets up the connections between UI components and the backend operations
        to ensure proper communication and functionality.
        """

        # update status
        self.__ops.op_signals.update_status.connect(self.status.set_status)

        # Group and category management
        self.categories.group.on_group_new.connect(self.__ops.on_create_group)
        self.categories.group.on_group_remove.connect(self.__ops.on_remove_group)
        self.categories.group.on_group_change.connect(self.__ops.ui_add_category)

        # Category operations
        self.categories.tree.on_create.connect(self.__ops.on_create_category)
        self.categories.tree.on_remove.connect(self.__ops.on_delete)
        self.categories.tree.on_rename.connect(self.__ops.on_rename_category)

        # Settings and preferences
        self.settings.preferences_grp.on_reset.connect(self.__ops.on_reset_preferences)
        self.actions_ui.on_settings.connect(self.__ops.on_open_settings)
        self.settings.preferences_grp.on_apply.connect(self.__ops.on_apply_preferences)

        # Thumbnail operations
        self.thumbnail.on_drop.connect(self.__ops.on_file_drop)
        self.thumbnail.on_drop_convert_mov.connect(self.__ops.convert_to_mov)
        self.thumbnail.on_open_in_explorer.connect(self.__ops.on_open_in_explorer)
        self.thumbnail.on_recache_proxy.connect(self.__ops.on_recache_proxy)

        # Tag management
        self.thumbnail.on_create_tag.connect(self.__ops.on_create_tag)
        self.thumbnail.on_add_tag.connect(self.__ops.on_add_tag)
        self.thumbnail.on_remove_tag.connect(self.__ops.on_remove_tag)

        # Category and filter changes
        self.categories.tree.on_change.connect(
            lambda group, category: self.__ops.on_change_category(
                group,
                category,
                tag=self.actions_ui.filters.current_tag,
                search_string=self.actions_ui.filters.search_text))

        self.thumbnail.on_delete_proxy.connect(
            lambda group, category, source_files, proxy_files: self.__ops.on_delete_proxy(
                group,
                category,
                source_files,
                proxy_files,
                self.actions_ui.filters.current_tag,
                self.actions_ui.filters.search_text)
        )

        self.actions_ui.filters.on_tags_filter_changed.connect(
            lambda tag, search_text: self.__ops.on_change_filters(
                self.categories.group.current_group,
                self.categories.tree.item_user_role,
                tag=tag,
                search_text=search_text))
        self.actions_ui.filters.on_change_search_text.connect(
            lambda tag, search_text: self.__ops.on_change_filters(
                self.categories.group.current_group,
                self.categories.tree.item_user_role,
                tag=tag,
                search_text=search_text))

        # Backend signals
        self.__ops.op_signals.execute_startup.connect(self.execute_on_startup)
        self.__ops.op_signals.on_files_dropped.connect(self.thumbnail.dropped_data)
        self.__ops.op_signals.on_recache_proxy.connect(self.thumbnail.dropped_data)
        self.__ops.op_signals.on_load_groups.connect(self.categories.group.add_groups)
        self.__ops.op_signals.on_load_categories.connect(self.categories.tree.add_categories)
        self.__ops.op_signals.on_change_category.connect(self.thumbnail.load_thumbnails)
        self.__ops.op_signals.thumbnail_scale.connect(self.thumbnail.update_thumbnail_scale)
        self.__ops.op_signals.on_open_settings.connect(self.settings.preferences_grp.update_pref_ui)
        self.__ops.op_signals.on_reset_preferences.connect(self.settings.preferences_grp.update_pref_ui)
        self.__ops.op_signals.on_render_completed.connect(self.thumbnail.on_render_completed)
        self.__ops.op_signals.on_start_conversion.connect(self.thumbnail.start_thread)
        self.__ops.op_signals.on_load_tags.connect(self.thumbnail.set_tags)
        self.__ops.op_signals.on_load_tags.connect(self.actions_ui.filters.add_tags)
        self.__ops.op_signals.on_change_filters.connect(self.thumbnail.load_thumbnails)

    def execute_on_startup(self):
        """
        Execute startup operations.
        This method initializes the UI by loading groups, categories, and tags,
        and updates the thumbnail scale based on user preferences.
        """
        self.__ops.ui_add_group()
        self.__ops.ui_add_category(self.categories.group.current_group)
        self.thumbnail.max_thread_count = int(self.__ops.data.preferences.thread_count)
        self.__ops.update_thumbnail_scale()
        self.__ops.on_load_tags()

    def event(self, event):
        """
        Handle custom events.

        :param event: The event to handle.
        :type event: QEvent
        :return: The result of the base class event handler.
        :rtype: bool
        """
        if not hasattr(event, 'type'):
            return

        if event.type() == QtCore.QEvent.Type.Show:
            try:
                set_widget_margins(self)
            except:
                pass
        return QtWidgets.QWidget.event(self, event)


def set_widget_margins(widget_object):
    if widget_object:
        target_widgets = set()
        target_widgets.add(widget_object.parentWidget().parentWidget())
        target_widgets.add(widget_object.parentWidget().parentWidget().parentWidget().parentWidget())

        for widget_layout in target_widgets:
            try:
                widget_layout.layout().setContentsMargins(0, 0, 0, 0)
            except Exception as error:
                print(error)


def main():
    main.e = Ulaavi()
    main.e.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    cm = Ulaavi()
    cm.show()
    try:
        app.exec()
    except:
        app.exec_()
