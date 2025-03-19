# -------------------------------- built-in Modules ----------------------------------
import os
import math

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2.QtWidgets import QTableWidget, QFrame, QMenu, QAction, QTableWidgetItem
    from PySide2.QtCore import Signal, Qt, QMimeData, QThreadPool, QRunnable, QCoreApplication
    from PySide2.QtGui import QIcon, QDrag
except ModuleNotFoundError:
    from PySide6.QtWidgets import QTableWidget, QFrame, QMenu, QTableWidgetItem
    from PySide6.QtCore import Signal, Qt, QMimeData, QThreadPool, QRunnable, QCoreApplication, QObject
    from PySide6.QtGui import QAction, QIcon, QDrag

# -------------------------------- Custom Modules ------------------------------------
from conversion.convert_mov import Signals
from . import _thumbnail
from data import config
from . import commonWidgets


class ThumbnailUI(QTableWidget):
    """
    Table widget to show thumbnails

    """
    on_drop = Signal(str, str, str)
    on_drag = Signal(str)
    on_add_preview = Signal(str, tuple)
    on_drop_convert_mov = Signal(str, str, bool, tuple, str, str)
    update_status = Signal(str)
    on_context_menu = Signal()
    on_open_in_explorer = Signal(str)
    on_recache_proxy = Signal(str, tuple, str, str)
    on_delete_proxy = Signal(str, str, list)

    on_create_tag = Signal(str)
    on_add_tag = Signal(str, str, list, str)
    on_remove_tag = Signal(str, str, list, str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.current_category = None
        self.current_group = None
        self.__tags = []
        self.cell_width = 0
        self.cell_height = 0
        self.rows = 0
        self.total_columns = 0
        self.__threadpool = QThreadPool()
        self.__threadpool.setMaxThreadCount(4)
        self.max_thread_count = 4
        self.thumbnail_scale = 1
        self.overlay_font_size = 10

        self.__total_files = 0
        self.__last_cell = (0, 0)

        self.__cell_position_updated = False
        self._set_widget_properties()

    def resizeEvent(self, event):
        self.calculate_column()

    def _set_widget_properties(self) -> None:
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

    def reset_attributes(self):
        self.rows = 0
        self.setRowCount(self.rows)
        self.__total_files = 0
        self.__last_cell = (0, 0)
        self.__cell_position_updated = False
        self.clear()

    def calculate_column(self):
        """
        calculate column count.
        :return: None.
        """
        self.total_columns = math.ceil(self.width() / self.cell_width) - 1
        self.setColumnCount(self.total_columns)

    def set_tags(self, tags: list):
        self.__tags = tags

    def update_thumbnail_scale(self, cell_width, cell_height, thumbnail_scale: float):
        self.thumbnail_scale = thumbnail_scale
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.calculate_column()

    def dragEnterEvent(self, event):
        """
        _summary_

        :param event: _description_
        :type event: _type_
        """
        if event.mimeData():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if not self.current_category:
            return

        if not event.mimeData().urls:
            return

        for url_ in event.mimeData().urls():
            self.on_drop.emit(url_.toLocalFile(), self.current_group, self.current_category)

    def mouseMoveEvent(self, event):
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

    def _context_menu(self, position) -> None:
        """
        context menu to perform additional operations
        """
        if not self.selectedItems():
            return

        file_directory = os.path.dirname(os.path.dirname(__file__))

        menu = QMenu(self)

        refresh_preview = menu.addAction(QIcon("{}/icons/recache.png".format(file_directory)), "Refresh Preview")
        delete_proxy = menu.addAction(QIcon("{}/icons/delete.png".format(file_directory)), "Delete Preview")

        menu.addSeparator()
        create_tag = menu.addAction(QIcon("{}/icons/fav.png".format(file_directory)), "Create Tag")

        add_tags_menu = QMenu(menu)
        add_tags_menu.setTitle('Add Tags')
        menu.addMenu(add_tags_menu)
        for i in self.__tags:
            tags_action = QAction(i, menu)
            tags_action.triggered.connect(lambda chk=False, item=i: self._add_tags(item))
            add_tags_menu.addAction(tags_action)


        added_tags = [tag for item in self.selectedItems() for tag in item.data(Qt.UserRole)['tags'] if tag]
        if added_tags:
            remove_tag_menu = QMenu(menu)
            remove_tag_menu.setTitle('Revove Tag')
            menu.addMenu(remove_tag_menu)
            for tag in added_tags:
                tags_action = QAction(tag, menu)
                tags_action.triggered.connect(lambda chk=False, item=i: self._remove_tag(tag))
                remove_tag_menu.addAction(tags_action)

        menu.addSeparator()

        open_in_explorer = menu.addAction(
            QIcon("{}/icons/explore.png".format(file_directory)), "Show in Explorer")

        refresh_preview.triggered.connect(self._recache_proxy)
        delete_proxy.triggered.connect(self._delete_proxy)
        open_in_explorer.triggered.connect(self._open_in_explorer)
        create_tag.triggered.connect(self._create_tag)

        menu.exec_(self.mapToGlobal(position))

    def _create_tag(self):
        tag, is_ok = commonWidgets.get_input_widget(title='Create Tag', label='Enter the Tag name:', parent=self)
        if is_ok:
            self.on_create_tag.emit(tag)

    def _add_tags(self, tag):
        selected_source_files = [item.data(Qt.UserRole)['source'] for item in self.selectedItems()]
        self._update_tag_in_overlay_label(tag)
        self.on_add_tag.emit(self.current_group, self.current_category, selected_source_files, tag)

    def _remove_tag(self, tag):
        selected_source_files = [item.data(Qt.UserRole)['source'] for item in self.selectedItems()]
        self.on_remove_tag.emit(self.current_group, self.current_category, selected_source_files, tag)

    def _open_in_explorer(self):
        selected_items = self.selectedItems()
        if 0 < len(selected_items) < 2:
            self.on_open_in_explorer.emit(selected_items[0].data(Qt.UserRole).get('source'))

    def _recache_proxy(self):
        for item in self.selectedItems():
            self.on_recache_proxy.emit(
                item.data(Qt.UserRole)['source'],
                (item.row(), item.column()),
                self.current_group,
                self.current_category)

    def _delete_proxy(self):
        self.on_delete_proxy.emit(
            self.current_group,
            self.current_category,
            [item.data(Qt.UserRole).get('source') for item in self.selectedItems()])

    def _update_tag_in_overlay_label(self, tag):
        for item in self.selectedItems():
            widget = self.cellWidget(item.row(), item.column())
            user_data= item.data(Qt.UserRole)
            user_data['tags'].append(tag)
            item.setData(Qt.UserRole, user_data)
            widget.set_metadata_overlay(user_data['metadata'], user_data['tags'])


    def start_thread(self, runnable_object):
        self.__threadpool.start(runnable_object)

    def dropped_data(self, dropped_files: list):
        for data in dropped_files:
            source_file, proxy_file, is_image_seq = data
            self._update_cell_positions(source_file)
            self._add_item(source_file, is_dropped=True)
            self.on_drop_convert_mov.emit(
                source_file, proxy_file, is_image_seq, self.__last_cell, self.current_group, self.current_category)

        self.disable_cells()

    def load_thumbnails(self, thumbnail_list: list):
        for data in thumbnail_list:
            self._update_cell_positions(data['source'])
            self._add_item(data, is_dropped=False)
            QCoreApplication.processEvents()
        self.disable_cells()

    def _update_cell_positions(self, dropped_file: list or str):
        if not dropped_file:
            return

        if not self.rowCount():
            self.setRowCount(1)

        elif self.__last_cell[1] + 1 == self.total_columns:
            self.setRowCount(self.rowCount() + 1)
            self.__last_cell = self.__last_cell[0] + 1, 0

        else:
            self.__last_cell = self.__last_cell[0], self.__last_cell[1] + 1

    def _add_item(self, data: dict or str, is_dropped: bool = False):
        if isinstance(data, dict):
            source_file = data['source']
            proxy_file = data['proxy']
        else:
            source_file = data

        self._ingest_cell_widget(self.__last_cell, source_file)
        thumbnail = _thumbnail.Thumbnails(self.cell_width, self.cell_height, is_dropped,
                                          source_file.endswith(config.supported_image_formats))
        thumbnail.set_font_size(self.thumbnail_scale)
        self.setCellWidget(self.__last_cell[0], self.__last_cell[1], thumbnail)

        if not is_dropped:
            thumbnail_image = proxy_file.replace('.mov', '.png') if proxy_file.endswith('.mov') \
                else proxy_file
            self.on_render_completed(data, thumbnail_image, cell_position=self.__last_cell)

    def disable_cells(self):
        """
        disable empty cells.
        :return: None.
        """
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                if self.item(row, col):
                    continue

                item = QTableWidgetItem()
                self.setItem(row, col, item)
                item.setFlags(Qt.NoItemFlags)

    def _ingest_cell_widget(self, position, file):
        """
        ingest src_file to widget item.
        :param tuple position: cell position.
        :param str file: source file.
        :return: None.
        """
        self.setColumnWidth(position[1], self.cell_width)
        self.setRowHeight(position[0], self.cell_height)
        widget_item = QTableWidgetItem()
        widget_item.setData(Qt.UserRole, file)
        self.setItem(position[0], position[1], widget_item)

    def on_render_completed(self, data: dict, thumbnail_image: str, cell_position: tuple):
        proxy_file = data['proxy']

        widget = self.cellWidget(*cell_position)
        widget.update_image_thumbnail(thumbnail_image)
        widget.set_metadata_overlay(data['metadata'], data['tags'])
        item = self.item(*cell_position)
        item.setData(Qt.UserRole, data)

        if proxy_file.endswith('.mov') and os.path.isfile(thumbnail_image):
            widget.update_video_thumbnail(proxy_file)
