"""
ThumbnailUI Module
==================

This module provides a custom QTableWidget implementation for displaying and managing thumbnails in a grid layout.
It supports features such as drag-and-drop, context menus, dynamic resizing, and thumbnail scaling. The module is designed
to be used in applications that require a visual representation of files (e.g., images, videos) with additional metadata
and tagging capabilities.

Key Features:
    - **Thumbnail Display**: Displays thumbnails in a grid layout with customizable cell dimensions.
    - **Drag-and-Drop Support**: Allows users to drag files into the widget and emits signals for handling dropped files.
    - **Context Menu**: Provides a context menu for actions like creating tags, adding/removing tags, refreshing proxies, and deleting proxies.
    - **Dynamic Resizing**: Automatically adjusts the number of columns based on the widget's width.
    - **Threading**: Utilizes a thread pool for asynchronous operations like thumbnail rendering.
    - **Signals**: Emits signals for various events such as file drops, drags, tag creation, and proxy updates.

Classes:
    - **ThumbnailUI**: The main class that implements the thumbnail display and management functionality.

Dependencies:
    - **PySide2/PySide6**: For Qt-based GUI components.
    - **os**: For file and directory operations.
    - **math**: For calculating column counts.
    - **importlib**: For dynamic module imports.
    - **sys**: For system-related operations.

"""

# -------------------------------- built-in Modules ----------------------------------
import math
import os
from typing import List, Tuple, Callable, Optional

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2.QtWidgets import QTableWidget, QFrame, QMenu, QAction, QTableWidgetItem
    from PySide2.QtCore import Signal, Qt, QMimeData, QThreadPool, QRunnable, QCoreApplication, QPoint
    from PySide2.QtGui import QIcon, QDrag
except ModuleNotFoundError:
    from PySide6.QtWidgets import QTableWidget, QFrame, QMenu, QTableWidgetItem
    from PySide6.QtCore import Signal, Qt, QMimeData, QThreadPool, QRunnable, QCoreApplication, QPoint
    from PySide6.QtGui import QAction, QIcon, QDrag

# -------------------------------- Custom Modules ------------------------------------
from . import _thumbnail
from data import config
from . import commonWidgets


class ThumbnailUI(QTableWidget):
    """
    A custom QTableWidget designed to display thumbnails with additional functionality such as drag-and-drop,
    context menus, and dynamic resizing.

    :Signals:
        - **on_drop**: Emitted when files are dropped onto the widget.
            - Args:
                - `file_path (str)`: The path of the dropped file.
                - `group (str)`: The current group.
                - `category (str)`: The current category.
        - **on_drag**: Emitted when files are dragged from the widget.
            - Args:
                - `data (str)`: The data being dragged.
        - **on_add_preview**: Emitted when a preview is added.
            - Args:
                - `file_path (str)`: The path of the file.
                - `position (tuple)`: The position of the preview.
        - **on_drop_convert_mov**: Emitted when a dropped file needs to be converted to MOV.
            - Args:
                - `source_file (str)`: The path of the source file.
                - `proxy_file (str)`: The path of the proxy file.
                - `is_image_seq (bool)`: Whether the file is part of an image sequence.
                - `cell_position (tuple)`: The position of the cell.
                - `group (str)`: The current group.
                - `category (str)`: The current category.
        - **update_status**: Emitted to update the status.
            - Args:
                - `status (str)`: The status message.
        - **on_context_menu**: Emitted when the context menu is requested.
        - **on_open_in_explorer**: Emitted to open a file in the explorer.
            - Args:
                - `file_path (str)`: The path of the file to open.
        - **on_recache_proxy**: Emitted to recache a proxy.
            - Args:
                - `source_file (str)`: The path of the source file.
                - `cell_position (tuple)`: The position of the cell.
                - `group (str)`: The current group.
                - `category (str)`: The current category.
        - **on_delete_proxy**: Emitted to delete a proxy.
            - Args:
                - `group (str)`: The current group.
                - `category (str)`: The current category.
                - `source_files (list)`: List of source files to delete.
                - `proxy_files (set)`: Set of proxy files to delete.
        - **on_create_tag**: Emitted to create a new tag.
            - Args:
                - `tag (str)`: The name of the tag to create.
        - **on_add_tag**: Emitted to add a tag to selected items.
            - Args:
                - `group (str)`: The current group.
                - `category (str)`: The current category.
                - `source_files (list)`: List of source files to tag.
                - `tag (str)`: The tag to add.
        - **on_remove_tag**: Emitted to remove a tag from selected items.
            - Args:
                - `group (str)`: The current group.
                - `category (str)`: The current category.
                - `source_files (list)`: List of source files to untag.
                - `tag (str)`: The tag to remove.
    """
    on_drop = Signal(str, str, str)
    on_drag = Signal(str)
    on_add_preview = Signal(str, tuple)
    on_drop_convert_mov = Signal(str, str, bool, tuple, str, str)
    update_status = Signal(str)
    on_context_menu = Signal()
    on_open_in_explorer = Signal(str)
    on_recache_proxy = Signal(str, tuple, str, str)
    on_delete_proxy = Signal(str, str, list, set)
    on_create_tag = Signal(str)
    on_add_tag = Signal(str, str, list, str)
    on_remove_tag = Signal(str, str, list, str)

    def __init__(self, parent=None):
        """
        Initialize the ThumbnailUI widget.

        :param parent: The parent widget.
        :type parent: QWidget, optional
        """
        super().__init__(parent=parent)
        self.current_category = None
        self.current_group = None
        self.__tags = []
        self.cell_width = 0
        self.cell_height = 0
        self.rows = 0
        self.total_columns = 0
        self.__threadpool = QThreadPool()
        self.max_thread_count = 4
        self.thumbnail_scale = 1
        self.overlay_font_size = 10

        self.__total_files = 0
        self.__last_cell = (0, 0)

        self.__cell_position_updated = False
        self._set_widget_properties()

    def resizeEvent(self, event) -> None:
        """
        Handle the resize event to recalculate the column count.

        :param event: The resize event.
        :type event: QResizeEvent
        """
        self.calculate_column()

    def _set_widget_properties(self) -> None:
        """
        Set the initial properties of the widget.
        """
        self.setGridStyle(Qt.NoPen)
        self.setContentsMargins(0, 0, 0, 0)
        self.setRowCount(self.rows)
        self.setColumnCount(self.total_columns)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setFocusPolicy(Qt.NoFocus)
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Plain)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._context_menu)

    def set_max_thread_count(self, thread_count: int) -> None:
        """
        set max thread count of QThreadPool.

        :param thread_count: thread count
        :type thread_count: int
        """
        self.__threadpool.setMaxThreadCount(thread_count)

    def reset_attributes(self) -> None:
        """
        Reset the attributes of the widget to their initial state.
        """
        self.rows = 0
        self.setRowCount(self.rows)
        self.__total_files = 0
        self.__last_cell = (0, 0)
        self.__cell_position_updated = False
        self.clear()

    def calculate_column(self) -> None:
        """
        Calculate the number of columns based on the widget's width and cell width.
        """
        self.total_columns = math.ceil(self.width() / self.cell_width) - 1
        self.setColumnCount(self.total_columns)

    def set_tags(self, tags: List[str]) -> None:
        """
        Set the list of tags available for the context menu.

        :param tags: List of tags.
        :type tags: list
        """
        self.__tags = tags

    def update_thumbnail_scale(self, cell_width: int, cell_height: int, thumbnail_scale: float) -> None:
        """
        Update the thumbnail scale and cell dimensions.

        :param cell_width: The width of each cell.
        :type cell_width: int
        :param cell_height: The height of each cell.
        :type cell_height: int
        :param thumbnail_scale: The scale factor for the thumbnails.
        :type thumbnail_scale: float
        """
        self.thumbnail_scale = thumbnail_scale
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.calculate_column()

    def dragEnterEvent(self, event) -> None:
        """
        Handle the drag enter event.

        :param event: The drag enter event.
        :type event: QDragEnterEvent
        """
        if event.mimeData():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event) -> None:
        """
        Handle the drag move event.

        :param event: The drag move event.
        :type event: QDragMoveEvent
        """
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event) -> None:
        """
        Handle the drop event.

        :param event: The drop event.
        :type event: QDropEvent
        """
        if not self.current_category:
            return

        if not event.mimeData().urls:
            return

        for url_ in event.mimeData().urls():
            self.on_drop.emit(url_.toLocalFile(), self.current_group, self.current_category)

    def mouseMoveEvent(self, event) -> None:
        """
        Handle the mouse move event to initiate a drag operation.

        :param event: The mouse move event.
        :type event: QMouseEvent
        """

        def get_user_data():
            for item in self.selectedItems():
                user_data = item.data(Qt.UserRole)
                if not user_data:
                    continue

                source_file = user_data.get('source')
                if not source_file:
                    continue

                yield str(source_file)

        data = '\n'.join(get_user_data())

        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(data)
        drag.setMimeData(mime_data)
        drag.exec_(Qt.MoveAction)

    def _context_menu(self, position: QPoint) -> None:
        """
        Display a context menu at the given position.

        :param position: The position to display the context menu.
        :type position: QPoint
        """
        if not self.selectedItems():
            return

        file_directory = os.path.dirname(os.path.dirname(__file__))

        menu = QMenu(self)
        create_tag = menu.addAction(QIcon("{}/icons/create_tag.png".format(file_directory)), "Create Tag")

        add_tags_menu = QMenu('Add Tags', menu)
        add_tags_menu.setIcon(QIcon("{}/icons/tags.png".format(file_directory)))
        menu.addMenu(add_tags_menu)
        for tag in self.__tags:
            tags_action = QAction(tag, add_tags_menu)
            tags_action.triggered.connect(lambda chk=False, item=tag: self._add_tags(item))
            add_tags_menu.addAction(tags_action)

        added_tags = [tag for item in self.selectedItems() for tag in item.data(Qt.UserRole)['tags'] if tag]
        if added_tags:
            remove_tag_menu = QMenu('Remove Tag', menu)
            remove_tag_menu.setIcon(QIcon("{}/icons/remove_tag.png".format(file_directory)))

            menu.addMenu(remove_tag_menu)
            for tag in added_tags:
                tags_action = QAction(tag, remove_tag_menu)
                tags_action.triggered.connect(lambda chk=False, item=tag: self._remove_tag(item))
                remove_tag_menu.addAction(tags_action)
        menu.addSeparator()

        refresh_preview = menu.addAction(QIcon("{}/icons/recache.png".format(file_directory)), "Refresh Proxy")
        delete_proxy = menu.addAction(QIcon("{}/icons/delete.png".format(file_directory)), "Delete Proxy")

        menu.addSeparator()

        open_in_explorer = menu.addAction(
            QIcon("{}/icons/explore.png".format(file_directory)), "Show in Explorer")

        refresh_preview.triggered.connect(self._recache_proxy)
        delete_proxy.triggered.connect(self._delete_proxy)
        open_in_explorer.triggered.connect(self._open_in_explorer)
        create_tag.triggered.connect(self._create_tag)

        menu.exec_(self.mapToGlobal(position))

    def _create_tag(self) -> None:
        """
        Create a new tag based on user input.
        """
        tag, is_ok = commonWidgets.get_input_widget(title='Create Tag', label='Enter the Tag name:', parent=self)
        if is_ok:
            self.on_create_tag.emit(tag)

    def _add_tags(self, tag: str) -> None:
        """
        Add a tag to the selected items.

        :param tag: The tag to add.
        :type tag: str
        """
        selected_source_files = [item.data(Qt.UserRole)['source'] for item in self.selectedItems()]
        self._update_tag_in_overlay_label(tag)
        self.on_add_tag.emit(self.current_group, self.current_category, selected_source_files, tag)

    def _remove_tag(self, tag: str) -> None:
        """
        Remove a tag from the selected items.

        :param tag: The tag to remove.
        :type tag: str
        """
        selected_source_files = [item.data(Qt.UserRole)['source'] for item in self.selectedItems()]
        self._update_tag_in_overlay_label(tag, action='remove')
        self.on_remove_tag.emit(self.current_group, self.current_category, selected_source_files, tag)

    def _open_in_explorer(self) -> None:
        """
        Open the selected item in the file explorer.
        """
        selected_items = self.selectedItems()
        if 0 < len(selected_items) < 2:
            self.on_open_in_explorer.emit(selected_items[0].data(Qt.UserRole).get('source'))

    def _recache_proxy(self) -> None:
        """
        Recache the proxy for the selected items.
        """
        for item in self.selectedItems():
            self.on_recache_proxy.emit(
                item.data(Qt.UserRole)['source'],
                (item.row(), item.column()),
                self.current_group,
                self.current_category)

    def _delete_proxy(self) -> None:
        """
        Delete the proxy for the selected items.
        """
        if commonWidgets.popup_message(
                'Delete Items', 'Are you sure want to delete the selected item(s)?', 'question'):

            proxy_files = set()
            source_files = []

            for item in self.selectedItems():
                source_files.append(item.data(Qt.UserRole).get('source'))
                proxy_files.add(item.data(Qt.UserRole).get('proxy'))

            self.on_delete_proxy.emit(
                self.current_group,
                self.current_category,
                source_files,
                proxy_files)

    def _update_tag_in_overlay_label(self, tag: str, action: str = 'add') -> None:
        """
        Update the tag in the overlay label of the selected items.

        :param tag: The tag to update.
        :type tag: str
        :param action: The action to perform ('add' or 'remove').
        :type action: str
        """
        for item in self.selectedItems():
            widget = self.cellWidget(item.row(), item.column())
            user_data = item.data(Qt.UserRole)
            if action == 'add' and tag not in user_data['tags']:
                user_data['tags'].append(tag)
            else:
                user_data['tags'].remove(tag)
            item.setData(Qt.UserRole, user_data)
            widget.set_metadata_overlay(user_data['metadata'], user_data['tags'])

    def start_thread(self, runnable_object: QRunnable) -> None:
        """
        Start a new thread using the thread pool.

        :param runnable_object: The runnable object to execute.
        :type runnable_object: QRunnable
        """
        self.__threadpool.start(runnable_object)

    def dropped_data(self, dropped_files: list):
        for data in dropped_files:
            source_file, proxy_file, is_image_seq = data
            self._update_cell_positions(source_file)
            self._add_item(source_file, is_dropped=True)
            self.on_drop_convert_mov.emit(
                source_file, proxy_file, is_image_seq, self.__last_cell, self.current_group, self.current_category)

        self._disable_cells()

    def load_thumbnails(self, thumbnail_list: List[dict], get_thumbnail_fn: Callable[[str], str]) -> None:
        """
        Load thumbnails from a list of data.

        :param thumbnail_list: List of thumbnail data.
        :type thumbnail_list: list
        :param get_thumbnail_fn: get thumbnail from proxy file callable function (from _utilities)
        :type get_thumbnail_fn: Callable
        """
        for data in thumbnail_list:
            self._update_cell_positions(data['source'])
            self._add_item(data, is_dropped=False, thumbnail_fn=get_thumbnail_fn)
            QCoreApplication.processEvents()
        self._disable_cells()

    def _update_cell_positions(self, dropped_file: list or str) -> None:
        """
        Update the cell positions based on the dropped file.

        :param dropped_file: The dropped file.
        :type dropped_file: list or str
        """
        if not dropped_file:
            return

        if not self.rowCount():
            self.setRowCount(1)

        elif self.__last_cell[1] + 1 == self.total_columns:
            self.setRowCount(self.rowCount() + 1)
            self.__last_cell = self.__last_cell[0] + 1, 0

        else:
            self.__last_cell = self.__last_cell[0], self.__last_cell[1] + 1

    def _add_item(self,
                  data: dict or str,
                  is_dropped: bool = False,
                  thumbnail_fn: Optional[Callable] = None) -> None:
        """
        Add an item to the table widget.

        :param data: The data to add.
        :type data: dict or str
        :param is_dropped: Whether the item is being dropped.
        :type is_dropped: bool
        """
        if isinstance(data, dict):
            # on render completed or when loading from json
            source_file = data.get('source', '')
            proxy_file = data.get('proxy', '')
        else:
            # on file drop
            proxy_file = ''
            source_file = data

        if not source_file:
            return

        self._ingest_cell_widget(self.__last_cell, source_file)
        thumbnail_widget = _thumbnail.Thumbnails(self.cell_width, self.cell_height, is_dropped,
                                                 source_file.endswith(config.SUPPORTED_IMAGE_FORMATS))
        thumbnail_widget.set_font_size(self.thumbnail_scale)
        self.setCellWidget(self.__last_cell[0], self.__last_cell[1], thumbnail_widget)

        if not is_dropped:
            thumbnail_image = thumbnail_fn(proxy_file)
            self.on_render_completed(data, thumbnail_image, cell_position=self.__last_cell)

    def _disable_cells(self) -> None:
        """"
        Disable empty cells in the table widget.
        """
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                if self.item(row, col):
                    continue

                item = QTableWidgetItem()
                self.setItem(row, col, item)
                item.setFlags(Qt.NoItemFlags)

    def _ingest_cell_widget(self, position: Tuple[int, int], source_file: str):
        """
        Ingest a file into a cell widget.

        :param position: The position of the cell.
        :type position: tuple
        :param source_file: The file to ingest.
        :type source_file: str
        """
        self.setColumnWidth(position[1], self.cell_width)
        self.setRowHeight(position[0], self.cell_height)
        widget_item = QTableWidgetItem()
        widget_item.setData(Qt.UserRole, source_file)
        self.setItem(position[0], position[1], widget_item)

    def on_render_completed(self, data: dict, thumbnail_image: str, cell_position: Tuple[int, int]) -> None:
        """
        Handle the completion of thumbnail rendering.

        :param data: The data associated with the thumbnail.
        :type data: dict
        :param thumbnail_image: The path to the thumbnail image.
        :type thumbnail_image: str
        :param cell_position: The position of the cell.
        :type cell_position: tuple
        """
        proxy_file = data['proxy']

        widget = self.cellWidget(*cell_position)
        widget.update_image_thumbnail(thumbnail_image)
        widget.set_metadata_overlay(data['metadata'], data['tags'])
        item = self.item(*cell_position)
        item.setData(Qt.UserRole, data)

        if proxy_file.endswith('.mov') and os.path.isfile(thumbnail_image):
            widget.update_video_thumbnail(proxy_file)
