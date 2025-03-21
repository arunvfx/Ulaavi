"""
Operations Module
=================

This module provides the core functionality for managing operations related to thumbnail generation, file handling,
and UI interactions. It includes classes for handling signals, managing data, and performing operations such as
file conversion, proxy creation, and tag management.

Key Features:
    - **Signal Management**: Uses `OpSignals` to emit signals for various UI and backend operations.
    - **File Handling**: Supports file drop events, proxy file creation, and file deletion.
    - **Tag Management**: Allows creating, adding, and removing tags from files.
    - **Thumbnail Scaling**: Dynamically adjusts thumbnail sizes and font scaling based on user preferences.
    - **Proxy Conversion**: Converts source files to proxy MOV files for efficient thumbnail generation.

Classes:
    - **OpSignals**: A QObject-based class that defines signals for communication between the UI and backend.
    - **Operations**: The main class that implements the core functionality for handling operations.

Dependencies:
    - **PySide2/PySide6**: For Qt-based signal and slot communication.
    - **os**: For file path manipulations.
    - **data.tool_data**: For managing tool-specific data and preferences.
    - **_utilities**: For utility functions like file handling and path resolution.
    - **conversion.convert_mov**: For converting files to MOV format.
    - **functools.partial**: For creating partial functions for signal connections.
"""

# -------------------------------- built-in Modules ----------------------------------
import os
from functools import partial
from typing import List, Tuple, Set

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2.QtCore import QObject, Signal, QRunnable
except ModuleNotFoundError:
    from PySide6.QtCore import QObject, Signal, QRunnable


# -------------------------------- Custom Modules ------------------------------------
from data import tool_data
import _utilities
from conversion import convert_mov


class OpSignals(QObject):
    """
    A QObject-based class that defines signals for communication between the backend operations and the UI.

    This class is used to emit signals for various events, such as thumbnail scaling, file handling,
    tag management, and proxy file conversion. These signals allow the UI to update dynamically based
    on backend operations.

    :Signals:
        - **execute_startup**: Emitted when the application starts up.
        - **thumbnail_scale**: Emitted to update thumbnail dimensions and font size.
            - Args:
                - `width (int)`: The width of the thumbnail.
                - `height (int)`: The height of the thumbnail.
                - `font_scale (float)`: The scaling factor for the font size.
        - **update_status**: Emitted to update the status bar message.
            - Args:
                - `message (str)`: The status message.
        - **on_load_groups**: Emitted to load groups into the UI.
            - Args:
                - `groups (tuple)`: A tuple of group names.
        - **on_load_categories**: Emitted to load categories into the UI.
            - Args:
                - `categories (tuple)`: A tuple of category names.
        - **on_change_category**: Emitted when the selected category changes.
            - Args:
                - `data (list)`: A list of thumbnail data for the selected category.
        - **on_load_tags**: Emitted to load tags into the UI.
            - Args:
                - `tags (list)`: A list of tag names.
        - **on_open_settings**: Emitted to open the settings panel.
            - Args:
                - `preferences (dict)`: A dictionary of current preferences.
        - **on_reset_preferences**: Emitted to reset preferences to default values.
            - Args:
                - `defaults (dict)`: A dictionary of default preferences.
        - **on_start_conversion**: Emitted to start the file conversion process.
            - Args:
                - `worker (object)`: The worker object responsible for conversion.
        - **on_files_dropped**: Emitted when files are dropped onto the UI.
            - Args:
                - `data (tuple)`: A tuple of file data (source, proxy, is_image_seq).
        - **on_recache_proxy**: Emitted to recache a proxy file.
            - Args:
                - `data (tuple)`: A tuple of file data (source, proxy, is_image_seq).
        - **on_render_completed**: Emitted when rendering of a proxy file is completed.
            - Args:
                - `data (dict)`: Metadata for the rendered file.
                - `thumbnail_path (str)`: Path to the rendered thumbnail.
                - `cell_position (tuple)`: The position of the cell in the UI.
        - **on_change_filters**: Emitted when filters (tags or search text) are changed.
            - Args:
                - `data (list)`: A list of filtered thumbnail data.
        - **on_delete_proxy**: Emitted to delete proxy files.
    """
    execute_startup = Signal()
    thumbnail_scale = Signal(int, int, float)
    update_status = Signal(str)
    on_load_groups = Signal(tuple)
    on_load_categories = Signal(tuple)
    on_change_category = Signal(list, object)
    on_load_tags = Signal(list)
    on_open_settings = Signal(dict)
    on_reset_preferences = Signal(dict)
    on_start_conversion = Signal(object)
    on_files_dropped = Signal(tuple)
    on_recache_proxy = Signal(tuple)
    on_render_completed = Signal(dict, str, tuple)
    on_change_filters = Signal(list, object)
    on_delete_proxy = Signal()


class Operations:
    """
    The main class responsible for managing core operations such as thumbnail scaling, file handling,
    tag management, and proxy file conversion. It interacts with the `tool_data.Data` class for data
    management and emits signals through the `OpSignals` class for UI updates.

    :ivar data: An instance of `tool_data.Data` for managing tool-specific data and preferences.
    :ivar op_signals: An instance of `OpSignals` for emitting signals to communicate with the UI.

    Notes:
        - This class relies on the `tool_data.Data` class for data persistence and retrieval.
        - Signals emitted by `op_signals` are used to update the UI and handle asynchronous operations.
    """

    def __init__(self):
        """Initialize the Operations class."""
        self.data = tool_data.Data()
        self.op_signals = OpSignals()

    def update_thumbnail_scale(self) -> None:
        """
        Update the thumbnail scale based on user preferences.
        Emits the `thumbnail_scale` signal with the calculated width, height, and font size.
        """
        default_width = 320
        font_size = 8

        self.op_signals.thumbnail_scale.emit(
            self._thumbnail_scale_percentage(default_width),
            self._thumbnail_scale_percentage(default_width / 1.89),
            self._scale_font_size(font_size))

    def _thumbnail_scale_percentage(self, initial_value: int) -> int:
        """
        Calculate the scaled thumbnail dimension based on user preferences.

        :param initial_value: The base dimension (width or height).
        :type initial_value: int
        :return: The scaled dimension.
        :rtype: int
        """
        return initial_value if self.data.preferences.thumbnail == 1 \
            else (0.25 * self.data.preferences.thumbnail * initial_value) + initial_value

    def _scale_font_size(self, initial_font_size: int) -> float:
        """
        Calculate the scaled font size based on user preferences.

        :param initial_font_size: The base font size.
        :type initial_font_size: int
        :return: The scaled font size.
        :rtype: float
        """
        return initial_font_size if self.data.preferences.thumbnail == 1 \
            else ((0.25 * self.data.preferences.thumbnail * 1) + 1) * initial_font_size

    def ui_add_group(self) -> None:
        """Load groups into the UI by emitting the `on_load_groups` signal."""
        self.op_signals.on_load_groups.emit(tuple(self.data.groups()))

    def ui_add_category(self, group: str) -> None:
        """
        Load categories for a specific group into the UI.

        :param group: The group name.
        :type group: str
            """
        if not group:
            return

        self.op_signals.on_load_categories.emit(tuple(self.data.categories(group)))

    def on_delete(self, group: str, category: str) -> None:
        """
        Delete a category from a group.

        :param group: The group name.
        :type group: str
        :param category: The category name.
        :type category: str
        """
        self.data.remove_category(group, category)
        self.op_signals.update_status.emit(f'Removed Category: {category} from Group: {group}')

    def on_create_group(self, group: str) -> None:
        """
        Create a new group.

        :param group: The group name.
        :type group: str
        """
        self.data.add_group(group)
        self.op_signals.update_status.emit(f'Created Group: {group}')

    def on_remove_group(self, group: str) -> None:
        """
        Remove a group.

        :param group: The group name.
        :type group: str
        """
        self.data.remove_group(group)
        self.op_signals.update_status.emit(f'Removed Group: {group}')

    def on_create_category(self, group: str, category: str) -> None:
        """
        Create a new category in a group.

        :param group: The group name.
        :type group: str
        :param category: The category name.
        :type category: str
        """
        self.data.add_category(group, category)
        self.op_signals.update_status.emit(f'Created Category: {category} in Group: {group}')

    def on_rename_category(self, group: str, old_category: str, new_category: str) -> None:
        """
        Rename a category in a group.

        :param group: The group name.
        :type group: str
        :param old_category: The current category name.
        :type old_category: str
        :param new_category: The new category name.
        :type new_category: str
        """
        self.data.rename_category(group, old_category, new_category)
        self.op_signals.update_status.emit(f'Renamed Category: {old_category} -> {new_category}')

    def on_change_category(self, group: str, category: str, tag: str = None, search_string: str = None):
        """
        Change the selected category and update the UI with the corresponding thumbnail data.

        :param group: The group name.
        :type group: str
        :param category: The category name.
        :type category: str
        :param tag: The tag to filter by (optional).
        :type tag: str
        :param search_string: The search string to filter by (optional).
        :type search_string: str
        """
        if category == 'root':
            return
        self.op_signals.on_change_category.emit(
            self.data.thumbnail_data(
                group, category, tag=tag, search_string=search_string), _utilities.get_thumbnail_from_proxy)

    def on_load_tags(self) -> None:
        """Load tags into the UI by emitting the `on_load_tags` signal."""
        self.op_signals.on_load_tags.emit(self.data.tags)

    def on_change_filters(self, group: str, category: str, tag: str = '', search_text: str = '') -> None:
        """
        Apply filters (tag and search text) to the thumbnail data and update the UI.

        :param group: The group name.
        :type group: str
        :param category: The category name.
        :type category: str
        :param tag: The tag to filter by (optional).
        :type tag: str
        :param search_text: The search text to filter by (optional).
        :type search_text: str
        """
        if category == 'root':
            return
        self.op_signals.on_change_filters.emit(
            self.data.thumbnail_data(
                group, category, tag=tag, search_string=search_text), _utilities.get_thumbnail_from_proxy)

    def on_create_tag(self, tag: str) -> None:
        """
        Create a new tag.

        :param tag: The tag name.
        :type tag: str
        """
        self.data.create_tag(tag)
        self.op_signals.update_status.emit(f'Created Tag: {tag}.')
        self.on_load_tags()

    def on_add_tag(self, group: str, category: str, source_files: List[str], tag: str) -> None:
        """
        Add a tag to the selected files.

        :param group: The group name.
        :type group: str
        :param category: The category name.
        :type category: str
        :param source_files: A list of source file paths.
        :type source_files: list
        :param tag: The tag to add.
        :type tag: str
        """
        self.data.add_tag(group, category, source_files, tag)

    def on_remove_tag(self, group: str, category: str, source_files: List[str], tag: str) -> None:
        """
        Remove a tag from the selected files.

        :param group: The group name.
        :type group: str
        :param category: The category name.
        :type category: str
        :param source_files: A list of source file paths.
        :type source_files: list
        :param tag: The tag to remove.
        :type tag: str
        """
        self.data.remove_tag(group, category, source_files, tag)

    def on_open_settings(self) -> None:
        """Open the settings panel by emitting the `on_open_settings` signal."""
        self.op_signals.on_open_settings.emit(self.data.preferences.preferences())
        self.op_signals.update_status.emit(f'Settings Panel')

    def on_reset_preferences(self) -> None:
        """Reset preferences to default values by emitting the `on_reset_preferences` signal."""
        self.op_signals.on_reset_preferences.emit(self.data.preferences.default_values())
        self.op_signals.update_status.emit(f'Settings Panel: reset preferences, click "Apply" to save the changes.')

    def on_apply_preferences(self, data: dict) -> None:
        """
        Apply updated preferences.

        :param data: A dictionary of updated preferences.
        :type data: dict
        """
        self.data.preferences.update(data)
        self.data.refresh()
        self.op_signals.execute_startup.emit()
        self.op_signals.update_status.emit(f'Settings Panel: Saved Preferences.')

    def on_file_drop(self, file_url: str, group: str, category: str) -> None:
        """
        Handle file drop events and initiate proxy file creation.

        :param file_url: The path of the dropped file.
        :type file_url: str
        :param group: The group name.
        :type group: str
        :param category: The category name.
        :type category: str
        """
        data = tuple(_utilities.get_dropped_files_with_proxy_path(
            file_path=file_url,
            proxy_root_path=self.data.preferences.proxy,
            group=group,
            category=category))

        if not data:
            self.op_signals.update_status.emit(f'Proxy already exist for the source file: {file_url}')

        self.op_signals.on_files_dropped.emit(data)

    def on_recache_proxy(self, file_url: str, cell_position: Tuple[int, int], group: str, category: str) -> None:
        """
        Recache a proxy file.

        :param file_url: The path of the source file.
        :type file_url: str
        :param cell_position: The position of the cell in the UI.
        :type cell_position: tuple
        :param group: The group name.
        :type group: str
        :param category: The category name.
        :type category: str
        """
        file_url = _utilities.get_source_file_path(file_url)

        data = tuple(_utilities.get_dropped_files_with_proxy_path(
            file_path=file_url,
            proxy_root_path=self.data.preferences.proxy,
            group=group,
            category=category))

        if not data:
            self.op_signals.update_status.emit(f'Proxy already exist for the source file: {file_url}')

        for i in data:
            self.convert_to_mov(*i, cell_position, group, category)

    def on_delete_proxy(self,
                        group: str,
                        category: str,
                        source_files: List[str],
                        proxy_files: Set[str],
                        tag: str = None,
                        search_string: str = None) -> None:
        """
        Delete proxy files and update the UI.

        :param group: The group name.
        :type group: str
        :param category: The category name.
        :type category: str
        :param source_files: A list of source file paths.
        :type source_files: list
        :param proxy_files: A set of proxy file paths.
        :type proxy_files: set
        :param tag: The tag to filter by (optional).
        :type tag: str
        :param search_string: The search string to filter by (optional).
        :type search_string: str
        """
        self.data.remove_data(group, category, source_files=source_files)
        self.on_change_category(group, category, tag, search_string)
        _utilities.delete_files([_utilities.get_proxy_thumbnail(proxy_file) for proxy_file in proxy_files])
        _utilities.delete_files(proxy_files)

    def convert_to_mov(self,
                       source_file: str,
                       proxy_file: str,
                       is_image_seq: bool,
                       cell_position: Tuple[int, int],
                       group: str,
                       category: str):
        """
        Convert a source file to a proxy MOV file.

        :param source_file: The path of the source file.
        :type source_file: str
        :param proxy_file: The path of the proxy file.
        :type proxy_file: str
        :param is_image_seq: Whether the file is part of an image sequence.
        :type is_image_seq: bool
        :param cell_position: The position of the cell in the UI.
        :type cell_position: tuple
        :param group: The group name.
        :type group: str
        :param category: The category name.
        :type category: str
        """
        if os.path.isfile(proxy_file):
            self.op_signals.update_status.emit(f'Proxy file already exist: {proxy_file}')
            return

        worker = convert_mov.ConvertMov(
            source_file, proxy_file, is_image_seq, self.data.preferences.res_width, self.data.preferences.res_height)
        self.op_signals.on_start_conversion.emit(worker)

        worker.signals.on_render_completed.connect(
            partial(self.on_render_completed,
                    group=group,
                    category=category,
                    source_file=source_file,
                    cell_position=cell_position))

        worker.signals.on_render_error.connect(self.on_render_error)
        self.op_signals.update_status.emit(f'Creating proxy File for {source_file}')

    def on_render_completed(self,
                            proxy_file: str,
                            proxy_thumbnail: str,
                            metadata: dict,
                            group: str,
                            category: str,
                            source_file: str,
                            cell_position: Tuple[int, int]) -> None:
        """
        Handle the completion of proxy file rendering.

        :param proxy_file: The path of the proxy file.
        :type proxy_file: str
        :param proxy_thumbnail: The path of the proxy thumbnail.
        :type proxy_thumbnail: str
        :param metadata: Metadata for the rendered file.
        :type metadata: dict
        :param group: The group name.
        :type group: str
        :param category: The category name.
        :type category: str
        :param source_file: The path of the source file.
        :type source_file: str
        :param cell_position: The position of the cell in the UI.
        :type cell_position: tuple
        """

        data = self.data.add_proxy_data(source_file, proxy_file, metadata, group, category)
        self.op_signals.on_render_completed.emit(data, proxy_thumbnail, cell_position)
        self.op_signals.update_status.emit(f'Created  Proxy File: {proxy_file}')

    def on_render_error(self, data: str) -> None:
        """
        Handle errors during proxy file rendering.

        :param data: The error data.
        :type data: Any
        """
        self.op_signals.update_status.emit(f'ERROR: {data}')

    @staticmethod
    def on_open_in_explorer(file_path: str) -> None:
        """
        Open the specified file path in the system file explorer.

        :param file_path: The path of the file to open.
        :type file_path: str
        """
        _utilities.open_in_explorer(file_path)
