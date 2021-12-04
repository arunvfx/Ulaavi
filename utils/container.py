# -*- coding: utf-8 -*-

import os
import sys
import re
import math
import json
import subprocess
from distutils import util

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *

from database.database import Database
from utils.settings import Settings
from utils.thumbnail import Thumbnail

from packages import pyseq

try:
    import nuke
    NUKE_VERSION = nuke.NUKE_VERSION_MAJOR
except Exception:
    pass

DIMENSION_X, DIMENSION_Y = 250, 180


class TableContent(QTableWidget):

    def __init__(self, width=None, height=None, current_category=None, top_level_category=None,
                 group=None, fav=False, d_type="all", search="", status_label=None, info=None,
                 info_status=None):
        """
        Table widget to load and modify  thumbnails.

        :param int width: width of the container.
        :param int height: height of the container.
        :param str current_category: currently selected sub-category name in the tree.
        :param str top_level_category: selected sub-category's parent name in the tree.
        :param str group: selected group name.
        :param bool fav: favourite button is checked or not.
        :param str d_type: selected filter name.
        :param str search: input of the user search.
        :param QLabel status_label: status bar label widget.
        :param QTextEdit info: info widget to load metadata.
        :param bool info_status: info button is checked or not.
        """
        super(TableContent, self).__init__()
        self.image_formats = [".jpg", ".jpeg", ".tiff", ".tif", ".png", ".tga", ".exr", ".dpx"]
        self.video_formats = [".mov", ".avi", ".mp4"]
        self.mesh_formats = [".obj", ".abc", ".fbx"]
        self.other_formats = self.video_formats + self.mesh_formats
        self.table_width = width
        self.table_height = height
        self.current_category = current_category
        self.top_level_category = top_level_category
        self.group = group
        self.favourite = fav
        self.d_type = d_type
        self.search = search.lower()
        self.status = status_label
        self.info_panel = info
        self.is_info = info_status
        self.dropped_files = []
        self.thumbnail = None
        self.thumb_height = 183
        self.thumb_width = 253
        self.cols = 0
        self.rows = 0
        self.total_file = 0
        self.last_cell = (0, 0)
        self.cell_position_updated = False
        self.img_seq = False

        self.settings = Settings().load_settings()
        self.ffmpeg, self.ffprobe = self.load_executables()
        self.thread_pool = QThreadPool()
        self.calculate_column()
        self.modify_table()
        self.load_thumbnail()

    def modify_table(self):
        """
        update table widget properties.
        :return: None.
        """
        self.resize(self.table_width, self.table_height)
        self.setGridStyle(Qt.NoPen)
        self.setContentsMargins(0, 0, 0, 0)
        self.setRowCount(self.rows)
        self.setColumnCount(self.cols)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setFocusPolicy(Qt.NoFocus)
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Plain)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)
        self.itemSelectionChanged.connect(
            lambda: self.metadata_selected_item(info=self.is_info)
        )

    def load_executables(self, mpeg=None, probe=None):
        """
        To load the abs path for ffmpeg and ffprobe.
        :param mpeg: None.
        :param probe: None.
        :return : absolute path of ffmpeg, ffprobe.
        """
        for file in os.listdir(self.settings["ffmpeg"]):
            if file.startswith("ffprobe"):
                probe = "{}/{}".format(self.settings["ffmpeg"], file)

            if file.startswith("ffmpeg"):
                mpeg = "{}/{}".format(self.settings["ffmpeg"], file)
        return mpeg, probe

    def calculate_column(self):
        """
        calculate column count.
        :return: None.
        """
        if NUKE_VERSION > 12:
            self.cols = math.ceil(self.table_width/self.thumb_width) - 1
        else:
            self.cols = math.ceil(self.table_width/self.thumb_width)

    @staticmethod
    def read_db():
        """
        load the database from data.json.
        :return dict: database.
        """
        db = Database()
        return db.read_from_json()

    def load_user_search(self, search):
        """
        load thumbnail based on user search input.
        :param str search: user search text.
        :return: None.
        """
        try:
            self.search = search
            self.load_thumbnail()
        except AttributeError:
            self.status_label("Select appropriate category!")

    def update_thumbnail_ui(self, width, height, fav, d_type):
        """
        reload thumbnails by favourites, search filters.
        :param int width: width of the container.
        :param int height: height of the container.
        :param bool fav: favourite button is enable or not.
        :param str d_type: selected filter name.
        :return: None.
        """
        try:
            self.favourite = fav
            self.table_width = width
            self.table_height = height
            self.d_type = d_type.lower()
            self.load_thumbnail()
        except RuntimeError:
            self.status_label("Select appropriate category!")

    def reset_values(self):
        """
        reset the values before thumbnail loads.
        :return: None.
        """
        self.clear()
        self.last_cell = (0, 0)
        self.cell_position_updated = False
        self.total_file = 0

    def status_label(self, data):
        """
        update status label.
        :param str data: string to show on label.
        :return: None.
        """
        self.status.setText("Total Files:{}".format(data))

    def dragEnterEvent(self, event):
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
        self.settings = Settings().load_settings()
        TableContent.read_db()
        if event.mimeData().urls:
            dropped_files = []
            event.setDropAction(Qt.CopyAction)
            
            for file in event.mimeData().urls():
                if os.path.splitext(file.toLocalFile())[1] in \
                        self.image_formats + self.other_formats:

                    if util.strtobool(self.settings["img_seq"]):
                        [dropped_files.append(j) for j in TableContent.validate_sequence(
                            file.toLocalFile(),
                            self.other_formats,
                            self.image_formats
                        )]
                    else:
                        dropped_files.append(file.toLocalFile())

            if self.current_category:
                dropped_files = self.validate_items_dropped_into_table(dropped_files)
                if dropped_files:
                    pos = self.calc_row_col_pos(dropped_files)
                    cell_position = self.cell_row_col_index(dropped_files, pos)
                    self.last_cell = self.load_cell_items(cell_position, dropped_files)
                    self.cell_position_updated = True

    @staticmethod
    def validate_sequence(file, other_formats, img_formats):
        """
        identify the dropped files has image sequence.
        :param str file: file need to validate for sequence.
        :param list other_formats:  movie and mesh formats as list.
        :param list img_formats: image formats.
        :return str: file.
        """
        if not os.path.isdir(file):
            if not os.path.splitext(file)[1] in other_formats and \
                    os.path.splitext(file)[1] in img_formats:

                file_seqs = pyseq.get_sequences(
                    "{}/{}*".format(
                        os.path.dirname(file), re.findall(r"\D+", os.path.basename(file))[0]
                    )
                )
                for seq in file_seqs:
                    if not os.path.isdir("{}/{}".format(os.path.dirname(file), seq)):
                        seq = seq.format("%h%p%t$$%r")
                        yield "{}/{}".format(os.path.dirname(file), seq)
            if os.path.splitext(file)[1] in other_formats:
                yield file

        else:
            file_seqs = pyseq.get_sequences(file)
            for seq in file_seqs:
                seq = seq.format("%h%p%t$$%r")
                if not os.path.isdir(file):
                    yield "{}/{}".format(os.path.dirname(file), seq)
                else:
                    yield "{}/{}".format(file, seq)

    def validate_items_dropped_into_table(self, dropped_files):
        """
        remove duplicate entries from the items dropped list.
        :param list dropped_files: dropped file list.
        :return list: dropped files list after remove duplicate entries.
        """
        TableContent.read_db()
        files_db = [item[0] for item in TableContent.query_items_by_filters(
            self.current_category,
            self.top_level_category,
            self.group,
            self.d_type,
            self.search
        )]
        return list(set(dropped_files).difference(files_db))
    
    @staticmethod
    def query_items_by_filters(current_category, top_level_cate, group, d_type="all", search=""):
        """
        filter thumbnails based on filter selected by user.
        :param str current_category: selected sub-category name.
        :param str top_level_cate: selected category name.
        :param str group: selected group name.
        :param str d_type: search filter type.
        :param str search: search text by user.
        :return tuple: cache_file_name, src_file_name, sub-category name, group name.
        """
        db = TableContent.read_db()[group][top_level_cate][current_category]

        for db_key, db_value in db.items():
            for key, value in db_value.items():
                
                if d_type == "stock" and \
                        not os.path.splitext(key)[1] in [".nk", ".obj", ".fbx", ".abc"] and \
                        (search == "" or search in os.path.basename(key).lower()):
                    yield str(key), str(value), current_category, str(db_key)

                elif d_type == "template" and key.endswith(".nk") and \
                        (search == '' or search in os.path.basename(key).lower()):
                    yield str(key), str(value), current_category, str(db_key)

                elif d_type == "mesh" and os.path.splitext(key)[1] in [".obj", ".fbx", ".abc"] and \
                        (search == "" or search in os.path.basename(key).lower()):
                    yield str(key), str(value), current_category, str(db_key)

                elif d_type == "all" and (search == '' or search in os.path.basename(key).lower()):
                    yield str(key), str(value), current_category, str(db_key)

    def calc_row_col_pos(self, files):
        """
        calculate rows and return the position of total cell positions as list.
        :param list files: file list to be loaded to widget.
        :return list: total row and column positions.
        """
        self.total_file += len(files)
        self.status_label(str(self.total_file))
        self.rows = math.ceil(self.total_file / self.cols)
        self.setRowCount(self.rows)
        return [(i, j) for i in range(int(self.rows)) for j in range(int(self.cols))]

    def cell_row_col_index(self, files, pos):
        """
        calculate the position for the files dropped.
        :param list files: list of files.
        :param list pos: position of the cells exists.
        :return list: dropped files positions.
        """
        if not self.cell_position_updated:
            return pos[pos.index(self.last_cell): len(files) + pos.index(self.last_cell)]
        else:
            return pos[pos.index(self.last_cell) + 1: len(files) + pos.index(self.last_cell) + 1]

    def load_thumbnail(self):
        """
        load caches to the widget s thumbnails.
        :return: None.
        """
        self.reset_values()
        last_cell_position = ()
        file_list = sorted([item for item in TableContent.query_items_by_filters(
            self.current_category, self.top_level_category, self.group, self.d_type, self.search)
                            if item[2] == self.current_category and
                            (item[1] == str(self.favourite) or item[1] == "True")])

        pos = self.calc_row_col_pos(file_list)
        count = 1

        try:
            cell_position = self.cell_row_col_index(file_list, pos)
            for position, f_tuple in zip(cell_position, file_list):
                if f_tuple:
                    try:
                        frame_length = int(f_tuple[0].split('$$')[1])
                        f_tuple = (f_tuple[0].split('$$')[0], f_tuple[1], f_tuple[2])
                    except Exception:
                        frame_length = None
                    cache = "{}/{}/{}/{}/{}".format(
                        self.settings["proxy"],
                        self.group,
                        self.top_level_category,
                        self.current_category,
                        f_tuple[3]
                    )
                    thumbnail = Thumbnail(
                        self,
                        item=cache,
                        source=os.path.basename(f_tuple[0])
                    )
                    self.ingest_cell_widget(position, f_tuple[0])
                    self.setCellWidget(position[0], position[1], thumbnail)

                    last_cell_position = (position[0], position[1])
                    count += 1
            self.cell_position_updated = True
            self.last_cell = last_cell_position
        except ValueError:
            self.status_label("0, No Items found in database!")
        except Exception as e:
            print(e)
        self.disable_cells()

    def disable_cells(self):
        """
        disable empty cells.
        :return: None.
        """
        for row in range(int(self.rows)):
            for col in range(int(self.cols)):
                if not self.item(row, col):
                    item = QTableWidgetItem()
                    self.setItem(row,col, item)
                    item.setFlags(Qt.NoItemFlags)

    def ingest_cell_widget(self, position, file):
        """
        ingest src_file to widget item.
        :param tuple position: cell position.
        :param str file: source file.
        :return: None.
        """
        self.setColumnWidth(position[1], self.thumb_width)
        self.setRowHeight(position[0], self.thumb_height)
        widget_item = QTableWidgetItem()
        widget_item.setData(Qt.UserRole, file)
        self.setItem(position[0], position[1], widget_item)

    def load_cell_items(self, cell_position, src_file):
        """
        load thumbnail to specific position in the widget once cache done.
        :param list cell_position: dropped items cell positions.
        :param list src_file: dropped file list.
        :return tuple: last cell position.
        """
        last_cell_position = ()
        for position, item in zip(cell_position, src_file):
            if item:
                try:
                    frame_length = item.split("$$")[1]
                    file_name = "{} {}".format(item.split("$$")[0], frame_length)
                except IndexError:
                    frame_length = None
                    file_name = item

                thumbnail = Thumbnail(
                    self,
                    True,
                    item=file_name,
                    source=os.path.basename(file_name)
                )

                if util.strtobool(self.settings["img_seq"]) or \
                        os.path.splitext(file_name)[1] in self.other_formats:
                    cache = "{}/{}/{}/{}/{}.gif".format(
                        self.settings["proxy"],
                        self.group,
                        self.top_level_category,
                        self.current_category,
                        os.path.splitext(os.path.basename(item))[0]
                    )
                else:
                    if not os.path.splitext(item)[1] in self.other_formats:
                        format_cache = os.path.splitext(os.path.basename(item))[0] + ".png"
                    else:
                        format_cache = os.path.splitext(os.path.basename(item))[0] + ".gif"
                    cache = "{}/{}/{}/{}/{}".format(
                        self.settings["proxy"],
                        self.group,
                        self.top_level_category,
                        self.current_category,
                        format_cache
                    )
                self.ingest_cell_widget(position, file_name)
                if os.path.splitext(file_name)[1] in self.mesh_formats:
                    self.thread_finished(
                        (file_name, "{}.png".format(os.path.splitext(cache)[0]), position)
                    )
                else:
                    self.execute_thread(item, position, cache, frame_length)
                    self.setCellWidget(position[0], position[1], thumbnail)

                last_cell_position = (position[0], position[1])
        self.disable_cells()
        return last_cell_position

    def execute_thread(self, item, pos, cache, frame_length):
        """
        run thread to convert files to gif
        :param str item: file to be converted.
        :param tuple pos: position of the cell.
        :param str cache: output 
        :param str frame_length: frame range.
        :return:
        """
        thread_run = ConvertGif(item, cache, pos, frame_length, self.ffmpeg)
        thread_run.conversion_signals.thread_finished.connect(self.thread_finished)
        self.thread_pool.start(thread_run)
        self.thread_pool.setMaxThreadCount(int(self.settings["threads"]))

    def thread_finished(self, data):
        """
        once cache done, ingest into data.json and load into widget.
        :param tuple data: gif converted  file data.
        :return: None.
        """
        QApplication.processEvents()
        try:
            if data[0].split("$$")[1].strip() == '':
                data = (data[0].split("$$")[0], data[1], data[2])
        except IndexError:
            pass
        Database().update_items_into_json(data[0],
                                          self.current_category,
                                          self.top_level_category,
                                          self.group,
                                          os.path.basename(data[1]))
        data = (data[0].split("$$")[0], data[1], data[2])
        thumbnail = Thumbnail(self, item=data[1], source=os.path.basename(data[0]))
        self.setCellWidget(data[2][0], data[2][1], thumbnail)

    def mouseMoveEvent(self, event):
        data = ''
        selection_array = []
        selected_cells = self.selectedItems()
        for item in selected_cells:
            file = item.data(Qt.UserRole)
            try:
                file = "{} {}".format(file.split("$$")[0], file.split("$$")[1])
            except IndexError as error:
                pass
            selection_array.append(str(file))
        for selection in selection_array:
            data += selection + '\n'
        drag = QDrag(self)
        mimedata = QMimeData()
        mimedata.setText(data)
        drag.setMimeData(mimedata)
        drag.start(Qt.MoveAction)

    def context_menu(self, pos):
        """
        context menu and its actions.
        :param QPoint pos: position of the cursor.
        :return: None.
        """
        sel_items = [item.data(Qt.UserRole) for item in self.selectedItems()]
        file_dir = os.path.dirname(os.path.dirname(__file__))

        if sel_items:
            self.menu = QMenu(self)
            db = TableContent.read_db()[self.group][self.top_level_category][self.current_category]
            fav_state = [v for key, value in db.items()
                         for k, v in value.items() if k in sel_items]

            metadata = self.menu.addAction(QIcon("{}/icons/info.png".format(file_dir)), 'Metadata')

            if 'False' in fav_state:
                favourite = self.menu.addAction(
                    QIcon("{}/icons/fav.png".format(file_dir)), "Add to Favourite"
                )
                favourite.triggered.connect(lambda: self.update_favourite_json(True))

            if "True" in fav_state:
                remove_favourite = self.menu.addAction(
                    QIcon("{}/icons/remove_fav.png".format(file_dir)), "Remove from Favourite"
                )
                remove_favourite.triggered.connect(lambda: self.update_favourite_json(False))

            sel_item = [item.data(Qt.UserRole)
                        for item in self.selectedItems()
                        if not os.path.splitext(item.data(Qt.UserRole))[1] in
                        [".abc", ".obj", ".fbx", ".nk"]]

            if sel_item:
                re_cache = self.menu.addAction(
                    QIcon("{}/icons/recache.png".format(file_dir)), "Recache"
                )
                re_cache.triggered.connect(self.re_cache)
                
            delete_cache = self.menu.addAction(
                QIcon("{}/icons/delete.png".format(file_dir)), "Delete"
            )
            delete_cache.triggered.connect(self.delete_confirmation)

            self.menu.addSeparator()

            explore = self.menu.addAction(
                QIcon("{}/icons/explore.png".format(file_dir)), "Show in Explorer"
            )
            explore.triggered.connect(lambda: TableContent.explore_file(sel_item))
            metadata.triggered.connect(lambda: self.metadata_selected_item(popup=True))

            self.menu.exec_(self.mapToGlobal(pos))

    def re_cache(self):
        """
        recache the selected items.
        :return: None
        """
        sel_items = [str(item.data(Qt.UserRole)) for item in self.selectedItems()]
        cell_position = [(self.indexFromItem(item).row(), self.indexFromItem(item).column())
                         for item in self.selectedItems()]
        self.load_cell_items(cell_position, sel_items)

    @staticmethod
    def explore_file(sel_item):
        """
        open selected files location in explorer/finder
        :param list sel_item: selected items list
        :return: None
        """
        import subprocess
        for item in sel_item:
            if len(item.split("$$")) > 1:
                item = os.path.dirname(item)
            if sys.platform == "win32":
                subprocess.Popen(r'explorer /select, "{}"' .format(item.strip().replace("/", "\\")))
            if sys.platform == "darwin":
                os.system("open '{}'".format(os.path.dirname(item)))
            if sys.platform == "linux2":
                os.system("xdg-open '{}'".format(os.path.dirname(item)))

    def delete_cache_db(self, dialog):
        """
        delete selected cache from database.
        :param QDialog dialog: dialog widget.
        :return: None.
        """
        dialog.close()
        db = TableContent.read_db()[self.group][self.top_level_category][self.current_category]
        sel_items = [item.data(Qt.UserRole) for item in self.selectedItems()]

        for db_key, db_value in db.items():
            for k, v in db_value.items():
                if k in sel_items:
                    Database().remove_item_from_json(self.current_category,
                                                     self.top_level_category,
                                                     self.group,
                                                     db_key)
                    cache = "{}/{}/{}/{}/{}".format(self.settings["proxy"],
                                                    self.group,
                                                    self.top_level_category,
                                                    self.current_category,
                                                    db_key)
                    if os.path.isfile(cache):
                        self.execute_remove_thread(cache)

        self.load_thumbnail()

    def delete_confirmation(self):
        """
        Popup dialog to confirm item deletion.
        :return: None.
        """
        dialog = QDialog(self)
        dialog.setObjectName("Remove Items")
        dialog.setStyleSheet("QDialog {background-color:  #323232;} "
                             "QLabel{border-radius: 5px; background-color:  #232323;} ")
        dialog.setFixedSize(500, 100)
        dialog.setWindowTitle("Warning")
        btn_delete = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_delete.accepted.connect(lambda: self.delete_cache_db(dialog))
        btn_delete.rejected.connect(dialog.close)
        label = QLabel("Are you sure want to delete the selected item(s)?")
        label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        layout = QVBoxLayout(dialog)
        layout.addWidget(label)
        layout.addWidget(btn_delete)
        dialog.show()

    def execute_remove_thread(self, item):
        """
        run thread to remove cache file from the drive.
        :param str item: file to be deleted.
        :return: None.
        """
        thread_run = RemoveCache(item)
        thread_run.remove_signals.remove_cache_running.connect(self.remove_cache_running)
        thread_run.remove_signals.remove_cache_finished.connect(self.remove_cache_finished)
        self.thread_pool.start(thread_run)
        self.thread_pool.setMaxThreadCount(int(self.settings["threads"]))

    def remove_cache_running(self, data):
        """
        update status label once remove thread started running.
        :param str data: remove file name.
        :return: None.
        """
        self.status_label("{}, Removing {}".format(self.total_file, data))

    def remove_cache_finished(self, data):
        """
        update status label once remove thread has finished.
        :param str data: removed file name.
        :return: None.
        """
        self.status_label("{}, {}".format(self.total_file, data))
        self.load_thumbnail()

    def update_favourite_json(self, fav):
        """
        update favourite into json.
        :param bool fav: enable/disable item favourite state.
        :return: None.
        """
        db = TableContent.read_db()[self.group][self.top_level_category][self.current_category]
        sel_items = [item.data(Qt.UserRole) for item in self.selectedItems()]
        for db_key, db_value in db.items():
            for src_file, fav_state in db_value.items():
                if src_file in sel_items:
                    Database().update_items_into_json(
                        src_file,
                        self.current_category,
                        self.top_level_category,
                        self.group,
                        db_key,
                        fav
                    )
        if self.favourite:
            self.load_thumbnail()

    def metadata_selected_item(self, popup=False, info=False):
        """
        load metadata to widget.
        :param bool popup: if true, load metadata in popup widget.
        :param bool info: if true, load metadata in info widget.
        :return: None.
        """
        self.is_info = info
        if popup or info:
            pos = QCursor.pos()
            if self.selectedItems():
                item = self.selectedItems()[-1].data(Qt.UserRole)
                try:
                    file = item.split("$$")[0].strip()
                    start_frame = item.split("$$")[1].split("-")[0]
                except IndexError:
                    file = item
                    start_frame = None

                metadata = self.query_metadata(file, start_frame)
                if popup:
                    self.info_widget = InfoPanel(metadata, pos)
                    self.info_widget.show()
                if info:
                    self.info_panel.setText(metadata)

    def query_metadata(self, src_file, start_frame=None):
        """
        metadata of the selected item.
        :param str src_file: source file.
        :param str start_frame: if image seq, start frame of the src file, else none.
        :return: src_file's metadata.
        """
        if start_frame:
            cmds = [
                self.ffprobe,
                "-loglevel",
                "0",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                "-start_number",
                start_frame,
                "-i",
                src_file,
                "-hide_banner"
            ]
        else:
            cmds = [
                self.ffprobe,
                "-loglevel",
                "0",
                "-print_format",
                "json",
                "-show_format",
                "-show_streams",
                src_file,
                "-hide_banner"
            ]

        process = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        meta_dict = json.loads(process.communicate()[0])
        metadata = ''
        count = 1
        meta_dict_new = {}
        for meta_key, meta_value in meta_dict.items():
            if isinstance(meta_value, list):
                for item in meta_value:
                    if isinstance(item, str):
                        item = json.loads(item)
                    if count == 1:
                        try:
                            metadata += "Dimension  : {} x {}\n".format(
                                str(item["width"]), item["height"]
                            )
                        except KeyError as error:
                            print("INFO: {} not found!".format(error))
                        try:
                            metadata += "Duration  : {} \n".format(item["duration"])
                        except KeyError as error:
                            print("INFO: {} not found!".format(error))

                        try:
                            metadata += "Frame(s)  : {}\n".format(item["nb_frames"])
                        except KeyError:
                            try:
                                metadata += "Frame(s)  : {}\n".format(item["duration_ts"])
                            except Exception as error:
                                print("INFO: {} not found!".format(error))
                        except Exception as error:
                            print(error)
                        count += 1
                        metadata += '-----------------------------------------------------------\n'
        metadata += json.dumps(meta_dict, indent=4)
        return metadata


# ---------------------------------------- Popup - Metadata --------------------------------------

class InfoPanel(QWidget):
    def __init__(self, metadata, pos):
        """
        metadata popup
        :param str metadata: metadata
        :param QPoint pos: Cursor position
        """
        super(InfoPanel, self).__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup)
        self.setContentsMargins(0, 0, 0, 0)
        self.resize(500, 320)
        h_layout = QHBoxLayout()
        text_edit = QTextEdit()
        text_edit.setMinimumSize(400, 300)
        text_edit.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        h_layout.addWidget(text_edit)
        self.setLayout(h_layout)
        text_edit.setText(metadata)
        self.move(QPoint(pos.x() - 500, pos.y()))


# --------------------------------------- GIF Conversion -----------------------------------------

class ConvertGif(QRunnable):

    def __init__(self, input_file, gif_file, pos, frame_length, ffmpeg):
        """
        Convert files in gif.
        :param str input_file: input file
        :param str gif_file: output gif file
        :param tuple pos: position of the cell
        :param str frame_length: frame range
        :param str ffmpeg: ffmpeg setup file
        """
        super(ConvertGif, self).__init__()
        self.ffmpeg = ffmpeg
        self.output = gif_file
        self.start_frame = None
        try:
            if isinstance(input_file.split("$$"), list):
                self.input, self.start_frame = input_file.split("$$")
        except ValueError:
            self.input = input_file
        if os.path.splitext(self.input)[1] in \
                [".exr", ".png", ".jpeg", ".jpg", ".tiff", ".tif"] and \
                (frame_length is None or frame_length.strip() == ''):
            self.output = os.path.splitext(self.output)[0] + ".png"
        self.item = input_file
        self.conversion_signals = ConversionSignal()
        self.pos = pos

    def run(self):
        """
        convert gif file
        :return: None
        """
        try:
            # remove gif file if already exists.
            if os.path.isfile(self.output):
                os.remove(self.output)
        except Exception as e:
            print(e)

        if not os.path.isfile(self.output):
            if not self.start_frame:
                cmds = [self.ffmpeg,
                        "-i",
                        self.input,
                        "-vf",
                        "scale={}:{}:force_original_aspect_ratio=decrease".format(
                            DIMENSION_X, DIMENSION_Y
                        ),
                        "-r",
                        "24",
                        self.output,
                        "-hide_banner"]
            else:
                cmds = [self.ffmpeg,
                        "-start_number",
                        self.start_frame.split('-')[0],
                        "-i",
                        self.input,
                        "-vf",
                        "scale={}:{}:force_original_aspect_ratio=decrease ".format(
                            DIMENSION_X, DIMENSION_Y
                        ),
                        "-r",
                        "24",
                        self.output,
                        "-hide_banner"]

            process = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            out, err = process.communicate()
            if out:
                self.conversion_signals.thread_finished.emit((self.item, self.output, self.pos))
            if err:
                print(err.decode())
        else:
            self.conversion_signals.thread_finished.emit((self.item, self.output, self.pos))


class RemoveCache(QRunnable):

    def __init__(self, cache):
        """
        TO remove cache file.
        :param str cache: cache file needs to be removed.
        """
        super(RemoveCache, self).__init__()
        self.remove_signals = RemoveSignal()
        self.cache = cache

    def run(self):
        """
        remove cache files and signal.
        """
        self.remove_signals.remove_cache_running.emit(self.cache)
        try:
            os.remove(self.cache)
            self.remove_signals.remove_cache_finished.emit(
                "cache(s) successfully deleted!"
            )
        except Exception as e:
            self.remove_signals.remove_cache_finished.emit(
                "Cannot remove cache(s), manually delete!"
            )


class ConversionSignal(QObject):
    thread_started = Signal(str)
    thread_finished = Signal(tuple)


class RemoveSignal(QObject):
    remove_cache_running = Signal(str)
    remove_cache_finished = Signal(str)
