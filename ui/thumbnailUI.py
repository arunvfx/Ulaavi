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


class ThumbnailUI(QtWidgets.QTableWidget):
    """
    Table widget to show thumbnails

    :param QtWidgets: _description_
    :type QtWidgets: _type_
    """
    on_drop = QtCore.Signal(str)
    on_drag = QtCore.Signal(str)
    on_add_preview = QtCore.Signal(str, tuple)
    on_drop_convert_mov = QtCore.Signal(str, str, tuple, bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.current_category = None
        self.cell_width = 0
        self.cell_height = 0
        self.rows = 0
        self.total_columns = 0
        self.threadpool = QtCore.QThreadPool()
        self.__total_files = 0
        self.__last_cell = (0, 0)

        self.__cell_position_updated = False
        self._set_widget_properties()

    # def resizeEvent(self, event):
    #     self.calculate_column()

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

    def reset_table(self):
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
        self.total_columns = math.ceil(self.width() / self.cell_width)
        self.setColumnCount(self.total_columns)

    def _context_menu(self, position) -> None:
        """
        context menu to perform additional operations
        """
        file_directory = os.path.dirname(os.path.dirname(__file__))

        menu = QtWidgets.QMenu(self)

        refresh_preview = menu.addAction(QtGui.QIcon("{}/icons/recache.png".format(file_directory)), "Refresh Preview")
        delete_preview = menu.addAction(QtGui.QIcon("{}/icons/delete.png".format(file_directory)), "Delete Preview")

        menu.addSeparator()
        favourite = menu.addAction(QtGui.QIcon("{}/icons/fav.png".format(file_directory)), "Add to Tag")
        favourite1 = menu.addAction(QtGui.QIcon("{}/icons/fav.png".format(file_directory)), "Create New Tag")
        menu.addSeparator()

        explore = menu.addAction(QtGui.QIcon("{}/icons/explore.png".format(file_directory)), "Show in Explorer")

        menu.exec_(self.mapToGlobal(position))

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
            self.on_drop.emit(url_.toLocalFile())

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

    def dropped_data(self, dropped_files: Generator):
        for data in dropped_files:
            source_file, proxy_file, is_image_seq = data
            self._update_cell_positions(source_file)
            self._add_item(source_file, os.path.basename(source_file), is_dropped=True)

            self.on_drop_convert_mov.emit(source_file, proxy_file, self.__last_cell, is_image_seq)

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

    def _add_item(self, source_file: str, proxy_file_name: str, is_dropped: bool = False):
        self._ingest_cell_widget(self.__last_cell, source_file)
        thumbnail = _thumbnail.Thumbnails(
            source_file, self.cell_width, self.cell_height, is_dropped)
        thumbnail.set_label(proxy_file_name)

        self.on_add_preview.emit(source_file, self.__last_cell)
        self.setCellWidget(self.__last_cell[0], self.__last_cell[1], thumbnail)

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

    def on_render_completed(self, data):
        print("INSDE COMPLETED: ", data)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    a = ThumbnailUI()
    a.show()
    app.exec_()
