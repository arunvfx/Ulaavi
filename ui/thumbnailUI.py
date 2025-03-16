# -------------------------------- built-in Modules ----------------------------------
import os
import math
from typing import Generator

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore, QtGui

# -------------------------------- Custom Modules ------------------------------------
from . import _thumbnail
from data import config


class ThumbnailUI(QtWidgets.QTableWidget):
    """
    Table widget to show thumbnails

    :param QtWidgets: _description_
    :type QtWidgets: _type_
    """
    on_drop = QtCore.Signal(str, str, str)
    on_drag = QtCore.Signal(str)
    on_add_preview = QtCore.Signal(str, tuple)
    on_drop_convert_mov = QtCore.Signal(str, str, bool, tuple, str, str)
    update_status = QtCore.Signal(str)
    on_context_menu = QtCore.Signal()
    on_open_in_explorer = QtCore.Signal(str)
    on_recache_proxy = QtCore.Signal(str, tuple, str, str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.current_category = None
        self.current_group = None
        self.__tags = []
        self.cell_width = 0
        self.cell_height = 0
        self.rows = 0
        self.total_columns = 0
        self.threadpool = QtCore.QThreadPool()
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
        self.setGridStyle(QtCore.Qt.NoPen)
        self.setContentsMargins(0, 0, 0, 0)
        self.setRowCount(self.rows)
        self.setColumnCount(self.total_columns)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setFrameShadow(QtWidgets.QFrame.Plain)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
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

    def update_thumbnail_scale(self, cell_width, cell_height, thumbnail_scale: int):
        self.thumbnail_scale = thumbnail_scale
        self.cell_width = cell_width
        self.cell_height = cell_height
        self.calculate_column()

    def _context_menu(self, position) -> None:
        """
        context menu to perform additional operations
        """
        self.on_context_menu.emit()
        file_directory = os.path.dirname(os.path.dirname(__file__))

        menu = QtWidgets.QMenu(self)

        refresh_preview = menu.addAction(QtGui.QIcon("{}/icons/recache.png".format(file_directory)), "Refresh Preview")
        delete_preview = menu.addAction(QtGui.QIcon("{}/icons/delete.png".format(file_directory)), "Delete Preview")

        menu.addSeparator()
        tags_menu = QtWidgets.QMenu(menu)
        tags_menu.setTitle('Add Tags')
        menu.addMenu(tags_menu)

        for i in self.__tags:
            tags_action = QtWidgets.QAction(i, menu)
            tags_action.triggered.connect(lambda chk=False, item=i: self.action_triggered(item))
            tags_menu.addAction(tags_action)

        create_new_tag = menu.addAction(QtGui.QIcon("{}/icons/fav.png".format(file_directory)), "Create Tag")
        menu.addSeparator()

        open_in_explorer = menu.addAction(
            QtGui.QIcon("{}/icons/explore.png".format(file_directory)), "Show in Explorer")

        refresh_preview.triggered.connect(self.recache_proxy)
        open_in_explorer.triggered.connect(self.open_in_explorer)
        # create_new_tag.triggered.connect()

        menu.exec_(self.mapToGlobal(position))

    def open_in_explorer(self):
        selected_items = self.selectedItems()
        if 0 < len(selected_items) < 2:
            self.on_open_in_explorer.emit(selected_items[0].data(QtCore.Qt.UserRole))

    def recache_proxy(self):
        self.item(0, 1).row()
        self.item(0, 1).column()
        for item in self.selectedItems():
            self.on_recache_proxy.emit(
                item.data(QtCore.Qt.UserRole), (item.row(), item.column()), self.current_group, self.current_category)

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
        data = ''
        selection_array = []
        selected_cells = self.selectedItems()

        for item in selected_cells:
            file = item.data(QtCore.Qt.UserRole)
            selection_array.append(str(file))

        for selection in selection_array:
            data += selection + '\n'

        drag = QtGui.QDrag(self)
        mime_data = QtCore.QMimeData()
        mime_data.setText(data)
        drag.setMimeData(mime_data)
        drag.exec_(QtCore.Qt.MoveAction)

    def add_tag(self, tag: str):
        self.tags_menu.addAction(tag)

    def start_thread(self, runnable_object: QtCore.QRunnable):
        self.threadpool.setMaxThreadCount(self.max_thread_count)
        self.threadpool.start(runnable_object)

    def dropped_data(self, dropped_files: Generator):
        for data in dropped_files:
            source_file, proxy_file, is_image_seq = data
            self._update_cell_positions(source_file)
            self._add_item(source_file, proxy_file, is_dropped=True)
            self.on_drop_convert_mov.emit(
                source_file, proxy_file, is_image_seq, self.__last_cell, self.current_group, self.current_category)

        self.disable_cells()

    def load_thumbnails(self, thumbnail_list: list):
        for data in thumbnail_list:
            source_file, proxy_file, metadata = data['source'], data['proxy'], data['metadata']
            self._update_cell_positions(source_file)
            self._add_item(source_file, proxy_file, metadata=metadata, is_dropped=False)
            QtCore.QCoreApplication.processEvents()
        self.disable_cells()

    def _update_cell_positions(self, dropped_file: list or str):
        if not dropped_file:
            return

        self._add_new_row()

    def _add_new_row(self):
        if not self.rowCount():
            self.setRowCount(1)

        elif self.__last_cell[1] + 1 == self.total_columns:
            self.setRowCount(self.rowCount() + 1)
            self.__last_cell = self.__last_cell[0] + 1, 0

        else:
            self.__last_cell = self.__last_cell[0], self.__last_cell[1] + 1

    def _add_item(self, source_file: str, proxy_file: str, metadata: dict or None = None, is_dropped: bool = False):
        self._ingest_cell_widget(self.__last_cell, source_file)
        thumbnail = _thumbnail.Thumbnails(self.cell_width, self.cell_height, is_dropped,
                                          source_file.endswith(config.supported_image_formats))

        thumbnail.set_font_size(10 * self.thumbnail_scale)
        self.setCellWidget(self.__last_cell[0], self.__last_cell[1], thumbnail)

        if not is_dropped:
            thumbnail_image = proxy_file.replace('.mov', '.png') if proxy_file.endswith('.mov') \
                else proxy_file
            self.on_render_completed(proxy_file, thumbnail_image, metadata=metadata, cell_position=self.__last_cell)

    def disable_cells(self):
        """
        disable empty cells.
        :return: None.
        """
        for row in range(self.rowCount()):
            for col in range(self.columnCount()):
                if self.item(row, col):
                    continue

                item = QtWidgets.QTableWidgetItem()
                self.setItem(row, col, item)
                item.setFlags(QtCore.Qt.NoItemFlags)

    def _ingest_cell_widget(self, position, file):
        """
        ingest src_file to widget item.
        :param tuple position: cell position.
        :param str file: source file.
        :return: None.
        """
        self.setColumnWidth(position[1], self.cell_width)
        self.setRowHeight(position[0], self.cell_height)
        widget_item = QtWidgets.QTableWidgetItem()
        widget_item.setData(QtCore.Qt.UserRole, file)
        self.setItem(position[0], position[1], widget_item)

    def on_render_completed(self, proxy_file: str, thumbnail_image: str, metadata: dict, cell_position: tuple):
        widget = self.cellWidget(*cell_position)
        widget.update_image_thumbnail(thumbnail_image)
        widget.set_label(metadata)

        if proxy_file.endswith('.mov') and os.path.isfile(thumbnail_image):
            widget.update_video_thumbnail(proxy_file)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    a = ThumbnailUI()
    a.show()
    app.exec_()
