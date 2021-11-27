# -*- coding: utf-8 -*-

from PySide2.QtWidgets import QTableWidget, QFrame, QTableWidgetItem, QMenu, QDialog, QDialogButtonBox, QLabel, \
    QVBoxLayout, QWidget, QGridLayout, QHBoxLayout, QTextEdit, QApplication, QGraphicsOpacityEffect, QProgressBar
from PySide2.QtGui import QDrag, QIcon, QMovie, QPixmap, QCursor
from PySide2.QtCore import *
import os
import sys
from settings import Settings
sys.path.append(os.path.dirname(__file__) + '/packages')
DIMENSION_X, DIMENSION_Y = 250, 180
import distutils
import re
import math
import subprocess
from database import Database
import pyseq
import json


class TableContent(QTableWidget):

    def __init__(self, width=None, height=None, progress=None, current_category=None, top_level_category=None,
                 group=None, fav=False, d_type='all', search='', status_label=None, info=None, info_status=None):
        super(TableContent, self).__init__()
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.horizontalHeader().setVisible(False)
        self.verticalHeader().setVisible(False)
        self.setFocusPolicy(Qt.NoFocus)
        self.setFrameShape(QFrame.NoFrame)
        self.setFrameShadow(QFrame.Plain)
        self.settings = Settings().load_settings()
        self.image_formats = ['.jpg', '.jpeg', '.tiff', '.tif', '.png', '.tga', '.exr']
        self.video_formats = ['.mov', '.avi', '.mp4']
        self.mesh_formats = ['.obj', '.abc', '.fbx']
        self.other_formats = self.video_formats + self.mesh_formats
        self.group = group
        self.current_category = current_category
        self.top_level_category = top_level_category
        self.progress_bar = progress
        self.d_type = d_type
        self.favourite = fav
        self.search = search.lower()
        self.status = status_label
        self.info_panel = info
        self.is_info = info_status
        self.setGridStyle(Qt.NoPen)
        self.setContentsMargins(0, 0, 0, 0)
        self.table_width = width
        self.table_height = height
        self.dropped_files = []
        self.thumb_height = 183
        self.thumb_width = 253
        self.cols = 0
        self.rows = 0
        self.cols = math.ceil(self.table_width/self.thumb_width)
        self.setRowCount(self.rows)
        self.setColumnCount(self.cols)
        self.total_file = 0
        self.last_cell = (0, 0)
        self.cell_position_updated = False
        self.img_seq = False
        self.ffmpeg, self.ffprobe = self.load_executables()
        self.load_items_to_ui()
        self.thread_pool = QThreadPool()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.context_menu)
        self.itemSelectionChanged.connect(lambda: self.metadata_selected_item(info=self.is_info))

    def load_executables(self, mpeg=None, probe=None):
        """
        return ffmpeg and ffprobe 
        """
        for file in os.listdir(self.settings['ffmpeg']):
            if file.startswith('ffprobe'):
                probe = '%s/%s' % (self.settings['ffmpeg'], file)
            if file.startswith('ffmpeg'):
                mpeg = '%s/%s' % (self.settings['ffmpeg'], file)
        return mpeg, probe

    @staticmethod
    def read_db():
        """
        return data from data.json 
        """
        db = Database()
        return db.read_from_json()

    def load_by_user_search(self, search):
        try:
            self.search = search
            self.clear()
            self.last_cell = (0,0)
            self.cell_position_updated = False
            self.load_items_to_ui()
        except AttributeError:
            self.status_label('Select appropriate category!')
        except Exception:
            pass

    def update_thumbnail_to_ui(self, width, height, fav, d_type):
        """
        refresh items in the widget
        """
        try:
            self.clear()
            self.last_cell = (0, 0)
            self.cell_position_updated = False
            self.favourite = fav
            self.table_width = width
            self.table_height = height
            self.d_type = d_type.lower()
            self.load_items_to_ui()
        except RuntimeError:
            self.status_label('Select appropriate category!')
        except Exception:
            pass

    def status_label(self, data):
        self.status.setText('Total Files:%s' % data)

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
        """
        drop items into widget
        """
        self.settings = Settings().load_settings()
        TableContent.read_db()

        if event.mimeData().urls:
            file = []
            event.setDropAction(Qt.CopyAction)

            for i in event.mimeData().urls():
                if os.path.splitext(i.toLocalFile())[1] in self.image_formats + self.other_formats:
                    if distutils.util.strtobool(self.settings['img_seq']):
                        [file.append(j) for j in TableContent.validate_sequence(i.toLocalFile(),
                                                                                self.other_formats,
                                                                                self.image_formats)]
                    else:
                        file.append(i.toLocalFile())

            if self.current_category:
                file = self.validate_items_dropped_into_table(file)
                if file:
                    self.total_file += len(file)
                    self.status_label(self.total_file)
                    self.rows = math.ceil(self.total_file/self.cols)
                    self.setRowCount(self.rows)
                    pos = [(i, j) for i in range(int(self.rows)) for j in range(int(self.cols))]

                    if not self.cell_position_updated:
                        cell_position = pos[pos.index(self.last_cell): len(file) + pos.index(self.last_cell)]
                    else:
                        cell_position = pos[pos.index(self.last_cell) + 1: len(file) + pos.index(self.last_cell) + 1]

                    self.last_cell = self.load_items_to_cell(cell_position, file)
                    self.cell_position_updated = True

    @staticmethod
    def validate_sequence(file, other_formats, img_formats):
        """
        check for image sequences
        """
        if not os.path.isdir(file):
            if not os.path.splitext(file)[1] in other_formats and \
                    os.path.splitext(file)[1] in img_formats:

                seq = pyseq.get_sequences('%s/%s*' % (os.path.dirname(file),
                                                      re.findall(r'[A-Za-z]+|\d+',
                                                                 os.path.basename(file))[0]
                                                      )
                                          )
                for f in seq:
                    f = f.format('%h%p%t$$%r')
                    yield '%s/%s' % (os.path.dirname(file), f)
            if os.path.splitext(file)[1] in other_formats:
                yield file
        else:
            seq = pyseq.get_sequences(file)
            for f in seq:
                f = f.format('%h%p%t$$%r')
                if not os.path.isdir(file):
                    yield '%s/%s' % (os.path.dirname(file), f)
                else:
                    yield '%s/%s' % (file, f)

    def validate_items_dropped_into_table(self, file):
        """
        return files as list by validate and remove any duplicates if exists
        """
        TableContent.read_db()
        files_db = [item[0] for item in TableContent.query_items_by_filters(self.current_category,
                                                                            self.top_level_category,
                                                                            self.group,
                                                                            self.d_type,
                                                                            self.search)]
        return list(set(file).difference(files_db))
    
    @staticmethod
    def query_items_by_filters(current_category, top_level_cate, group, d_type='all', search=''):
        """
        return items from data.json based on filters selected
        """
        db = TableContent.read_db()[group][top_level_cate][current_category]

        for k, val in db.items():
            for key, value in val.items():
                if d_type == 'stock' and not os.path.splitext(key)[1] in ['.nk', '.obj', '.fbx', '.abc'] and \
                        (search == '' or search in os.path.basename(key).lower()):
                    yield str(key), str(value), current_category, str(k)

                elif d_type == 'template' and key.endswith('.nk') and \
                        (search == '' or search in os.path.basename(key).lower()):
                    yield str(key), str(value), current_category, str(k)

                elif d_type == 'mesh' and os.path.splitext(key)[1] in ['.obj', '.fbx', '.abc'] and \
                        (search == '' or search in os.path.basename(key).lower()):
                    yield str(key), str(value), current_category, str(k)

                elif d_type == 'all'and (search == '' or search in os.path.basename(key).lower()):
                    yield str(key), str(value), current_category, str(k)

    def load_items_to_ui(self):
        """
        load items into widget as thumbnails
        """
        file = [item for item in TableContent.query_items_by_filters(
            self.current_category, self.top_level_category, self.group, self.d_type, self.search)
                if item[2] == self.current_category and (item[1] == str(self.favourite) or item[1] == 'True')]

        self.total_file = len(file)
        self.status_label(self.total_file)

        self.rows = math.ceil(self.total_file / self.cols)
        self.setRowCount(self.rows)
        pos = [(i, j) for i in range(int(self.rows)) for j in range(int(self.cols))]
        count = 1
        try:
            if not self.cell_position_updated:
                cell_position = pos[pos.index(self.last_cell): len(file) + pos.index(self.last_cell)]
            else:
                cell_position = pos[pos.index(self.last_cell) + 1: len(file) + pos.index(self.last_cell) + 1]

            for position, f_tuple in zip(cell_position, file):
                if f_tuple:
                    try:
                        frame_length = int(f_tuple[0].split('$$')[1])
                        f_tuple = (f_tuple[0].split('$$')[0], f_tuple[1], f_tuple[2])
                    except Exception:
                        frame_length = None

                    cache = '%s/%s/%s/%s/%s' % (self.settings['proxy'],
                                                self.group,
                                                self.top_level_category,
                                                self.current_category,
                                                f_tuple[3])
                    source = [
                        i for i in
                        TableContent.read_db()[self.group][self.top_level_category][self.current_category][f_tuple[3]]
                    ]
                    self.setColumnWidth(position[1], self.thumb_width)
                    self.setRowHeight(position[0], self.thumb_height)

                    self.thumb = Thumbnail(self,
                                           item=cache,
                                           source=os.path.basename(source[0]),
                                           frame_length=frame_length)

                    widget_item = QTableWidgetItem()
                    widget_item.setData(Qt.UserRole, f_tuple[0])
                    self.setItem(position[0], position[1], widget_item)
                    self.setCellWidget(position[0], position[1], self.thumb)
                    last_cell_position = (position[0], position[1])
                    self.load_progress(count, self.total_file)
                    count += 1
            self.cell_position_updated = True
            self.last_cell = last_cell_position
        except ValueError:
            self.status_label('0, No Items found in database!')
        except Exception as e:
            print(e)

    def load_progress(self, count, total):
        progress = int((float(count) / total) * 100)
        self.progress_bar.setValue(progress)
        if not progress % 100:
            self.progress_bar.setVisible(False)
        else:
            self.progress_bar.setVisible(True)

    def load_items_to_cell(self, cell_position, file):
        """
        load thumbnail to specific position in the widget once cache done
        """
        for position, item in zip(cell_position, file):
            if item:
                try:
                    frame_length = item.split('$$')[1]
                    input = item.split('$$')[0]
                except Exception:
                    frame_length = None
                    input = item

                self.setColumnWidth(position[1], self.thumb_width)
                self.setRowHeight(position[0], self.thumb_height)
                self.thumbnail = Thumbnail(self,
                                           True,
                                           item=input,
                                           source=os.path.basename(input),
                                           frame_length=frame_length)

                if distutils.util.strtobool(self.settings['img_seq']) or \
                        os.path.splitext(input)[1] in self.other_formats:
                    output = '%s/%s/%s/%s/%s.gif' % (self.settings['proxy'],
                                                     self.group,
                                                     self.top_level_category,
                                                     self.current_category,
                                                     os.path.splitext(os.path.basename(item))[0])
                else:
                    if not os.path.splitext(item)[1] in self.other_formats:
                        format_cache = os.path.splitext(os.path.basename(item))[0] + '.png'
                    else:
                        format_cache = os.path.splitext(os.path.basename(item))[0] + '.gif'
                    output = '%s/%s/%s/%s/%s' % (self.settings['proxy'],
                                                 self.group,
                                                 self.top_level_category,
                                                 self.current_category,
                                                 format_cache)

                if not os.path.splitext(input)[1] in self.mesh_formats:
                    self.execute_thread(item, position, output, frame_length)
                else:
                    self.thread_finished((input, os.path.splitext(output)[0] + '.png', position))

                widget_item = QTableWidgetItem()
                widget_item.setData(Qt.UserRole, input)
                self.setItem(position[0], position[1], widget_item)
                self.setCellWidget(position[0], position[1], self.thumbnail)
                last_cell_position = (position[0], position[1])
        return last_cell_position

    def execute_thread(self, item, pos, output, frame_length):
        """
        initiate gif conversion
        """
        thread_run = ConvertGif(item, output, pos, frame_length, self.ffmpeg)
        thread_run.conversion_signals.thread_finished.connect(self.thread_finished)
        self.thread_pool.start(thread_run)
        self.thread_pool.setMaxThreadCount(int(self.settings['threads']))

    def thread_finished(self, item):
        """
        once cache done, ingest into data.json and load into widget
        """
        Database().update_items_into_json(item[0],
                                          self.current_category,
                                          self.top_level_category,
                                          self.group,
                                          os.path.basename(item[1]))
        try:
            frame_length = int(item[0].split('$$')[1])
            item = (item[0].split('$$')[0], item[1], item[2])
        except Exception:
            frame_length = None

        try:
            self.thumbnail = Thumbnail(self, item=item[1], source=os.path.basename(item[0]), frame_length=frame_length)
            self.setCellWidget(item[2][0], item[2][1], self.thumbnail)
        except Exception:
            pass

    def mouseMoveEvent(self, event):
        selection_array = []
        selected_cells = self.selectedItems()
        for item in selected_cells:
            text = item.data(Qt.UserRole)
            try:
                text = text.split('$$')[0] + ' %s' % text.split('$$')[1]
            except Exception:
                pass
            selection_array.append(str(text))
        data = ''
        for selection in selection_array:
            data += selection + '\n'
        drag = QDrag(self)
        data = TableContent.query_mimedata(data)
        drag.setMimeData(data)
        drag.start(Qt.MoveAction)

    @staticmethod
    def query_mimedata(data):
        mimeData = QMimeData()
        mimeData.setText(data)
        return mimeData

    def context_menu(self, pos):
        sel_items = [item.data(Qt.UserRole) for item in self.selectedItems()]
        if sel_items:
            self.menu = QMenu(self)
            db = TableContent.read_db()[self.group][self.top_level_category][self.current_category]            
            fav_state = [v for key, value in db.items() for k, v in value.items() if k in sel_items]            
            metadata = self.menu.addAction(QIcon(os.path.dirname(__file__) + '/icons/info.png'), 'Metadata')

            if 'False' in fav_state:
                favourite = self.menu.addAction(QIcon(os.path.dirname(__file__) + '/icons/fav.png'), 'Add to Favourite')
                favourite.triggered.connect(lambda: self.toggle_fav_state(True))
            if 'True' in fav_state:
                remove_favourite = self.menu.addAction(
                    QIcon(os.path.dirname(__file__) + '/icons/remove_fav.png'), 'Remove from Favourite')
                remove_favourite.triggered.connect(lambda: self.toggle_fav_state(False))

            sel_item = [item.data(Qt.UserRole) for item in self.selectedItems()
                        if not os.path.splitext(item.data(Qt.UserRole))[1] in ['.abc', '.obj', '.fbx', '.nk']]
            if sel_item:
                recache = self.menu.addAction(QIcon(os.path.dirname(__file__) + '/icons/recache.png'),'Recache')
                recache.triggered.connect(self.re_cache)
                
            delete_cache = self.menu.addAction(QIcon(os.path.dirname(__file__) + '/icons/delete.png'), 'Delete')
            delete_cache.triggered.connect(self.delete_confirmation)

            self.menu.addSeparator()
            explore = self.menu.addAction(QIcon(os.path.dirname(__file__) + '/icons/explore.png'), 'Show in Explorer')
            explore.triggered.connect(lambda: TableContent.explore_file(sel_item))
            
            metadata.triggered.connect(lambda: self.metadata_selected_item(popup=True))
            
            self.menu.exec_(self.mapToGlobal(pos))

    def re_cache(self):
        sel_items = [str(item.data(Qt.UserRole)) for item in self.selectedItems()]
        cell_position = [(self.indexFromItem(i).row(), self.indexFromItem(i).column()) 
                         for i in self.selectedItems()]
        self.load_items_to_cell(cell_position, sel_items)

    @staticmethod
    def explore_file(sel_item):
        import subprocess
        for item in sel_item:
            if sys.platform == 'win32':
                subprocess.Popen(r'explorer /select, "%s"' % item.replace('/', '\\'))
            if sys.platform == 'darwin':
                os.system('open "%s"' % os.path.dirname(item))
            if sys.platform == 'linux2':
                os.system('xdg-open "%s"' % os.path.dirname(item))

    def delete_cache_db(self, dialog):
        dialog.close()
        db = TableContent.read_db()[self.group][self.top_level_category][self.current_category]
        sel_items = [item.data(Qt.UserRole) for item in self.selectedItems()]

        for key, value in db.items():
            for k, v in value.items():
                if k in sel_items:
                    Database().remove_item_from_json(self.current_category,
                                                     self.top_level_category,
                                                     self.group,
                                                             key)
                    cache = '{}/{}/{}/{}/{}' .format(self.settings['proxy'],
                                                     self.group,
                                                     self.top_level_category,
                                                     self.current_category,
                                                     key)
                    if os.path.isfile(cache):
                        self.execute_remove_thread(cache)

        self.last_cell = (0, 0)
        self.cell_position_updated = False
        self.clear()
        self.load_items_to_ui()

    def delete_confirmation(self):
        dialog = QDialog(self)
        dialog.setObjectName('Remove Items')
        dialog.setStyleSheet('QDialog {background-color:  #323232;} '
                             'QLabel{border-radius: 5px; background-color:  #232323;} ')
        dialog.setFixedSize(500, 100)
        dialog.setWindowTitle('Warning')
        btn_delete = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_delete.accepted.connect(lambda: self.delete_cache_db(dialog))
        btn_delete.rejected.connect(dialog.close)
        label = QLabel('Are you sure want to delete the selected item(s)?')
        label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        layout = QVBoxLayout(dialog)
        layout.addWidget(label)
        layout.addWidget(btn_delete)
        dialog.show()

    def execute_remove_thread(self, item):
        thread_run = RemoveCache(item)
        thread_run.remove_signals.remove_cache_running.connect(self.remove_cache_running)
        thread_run.remove_signals.remove_cache_finished.connect(self.remove_cache_finished)
        self.thread_pool.start(thread_run)
        self.thread_pool.setMaxThreadCount(int(self.settings['threads']))

    def remove_cache_running(self, state):
        self.status_label('{}, Removing {}' .format(self.total_file, state))

    def remove_cache_finished(self, data):
        self.status_label('{}, {}'.format(self.total_file, data))
        self.load_items_to_ui()

    def toggle_fav_state(self, fav):
        db = TableContent.read_db()[self.group][self.top_level_category][self.current_category]
        sel_items = [item.data(Qt.UserRole) for item in self.selectedItems()]
        for key, value in db.items():
            for k, v in value.items():
                if k in sel_items:
                    Database().update_items_into_json(k,
                                                      self.current_category,
                                                      self.top_level_category,
                                                      self.group,
                                                      key,
                                                      fav)
        if fav is False and self.favourite:
            self.last_cell = (0, 0)
            self.cell_position_updated = False
            self.clear()
            self.load_items_to_ui()

    def metadata_selected_item(self, popup=False, info=False):
        """
        load metadata on popup/info widget
        """
        self.is_info = info
        if popup or info:
            pos = QCursor.pos()
            if self.selectedItems():
                item = self.selectedItems()[-1].data(Qt.UserRole)
                try:
                    file = item.split('$$')[0].strip()
                    start_frame = item.split('$$')[1].split('-')[0]
                except Exception:
                    file = item
                    start_frame = None
                metadata = self.get_metadata(file, start_frame)
                if popup:
                    self.info_widget = InfoPanel(metadata, pos)
                    self.info_widget.show()
                if info:
                    self.info_panel.setText(metadata)

    def get_metadata(self, input, start_frame=None):
        """
        return metadata of the selected item
        """
        if start_frame:
            cmds = [self.ffprobe, '-loglevel', '0', '-print_format', 'json', '-show_format', '-show_streams',
                    '-start_number', start_frame, '-i', input, '-hide_banner']
        else:
            cmds = [self.ffprobe, '-loglevel', '0', '-print_format', 'json', '-show_format', '-show_streams',
                    input, '-hide_banner']
        process = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        meta_dict = json.loads(process.communicate()[0].decode())
        metadata = ''

        for k, v in meta_dict.items():
            if isinstance(v, list):
                for item in v:
                    if isinstance(item, str):
                        try:
                            item = json.loads(item)
                        except Exception:
                            pass
                    metadata += 'Dimension  : {} x {}\n'.format(item['width'],item['height'] )
                    try:
                        metadata += 'Duration  : {} \n'.format(item['duration'])
                    except Exception:
                        pass
                    try:
                        metadata += 'Frame(s)  : {}\n'.format(item['nb_frames'])
                    except KeyError:
                        try:
                            metadata += 'Frame(s)  : {}\n'.format(item['duration_ts'])
                        except Exception:
                            pass
                    except Exception:
                        pass
                    metadata += '--------------------------------------------------------------------\n'
        metadata += json.dumps(meta_dict, indent=4)
        return metadata


# ---------------------------------------- Popup - Metadata -----------------------------------------------------------
class InfoPanel(QWidget):
    def __init__(self, metadata, pos):
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


# ------------------------------------------ Thumbnail ----------------------------------------------------------------
class Thumbnail(QWidget):

    def __init__(self, parent, *drop, **data):
        super(Thumbnail, self).__init__(parent)
        item, source, self.drop = str(data['item']), data['source'], drop
        if os.path.splitext(source)[1] in ['.obj', '.abc', '.fbx']:
            item = os.path.dirname(__file__) + '/icons/obj.png'
        if os.path.splitext(source)[1] in ['.nk']:
            item = os.path.dirname(__file__) + '/icons/nuke_1.png'
        layout = QGridLayout()
        self.label = QLabel()
        self.label.setGeometry(0, 0, 250, 180)
        self.label1 = QLabel()
        self.label1.setAlignment(Qt.AlignHCenter)
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.label1.setMaximumHeight(20)
        self.load_gif(item)
        try:
            current_item = os.path.basename(source).split('$$')[0]
        except Exception:
            current_item = os.path.basename(source)
        self.label1.setText(current_item)
        self.label1.setStyleSheet('QLabel{color:rgb(160, 160, 160, 160);}')
        self.setMaximumWidth(250)
        layout.addWidget(self.label)
        layout.addWidget(self.label1)
        QApplication.processEvents()
        self.setLayout(layout)

    def load_gif(self, item):
        if self.drop:
            self.movie = QMovie(os.path.dirname(__file__) + '/icons/processing.gif')
            self.movie.setCacheMode(QMovie.CacheAll)
            size = self.movie.scaledSize()
            self.label.setMovie(self.movie)
            self.label.setGeometry(0, 0, size.width(), size.height())
            self.movie.jumpToFrame(0)
            self.opacity = QGraphicsOpacityEffect()
            self.opacity.setOpacity(0.3)
            self.label.setGraphicsEffect(self.opacity)
            self.movie.start()
        else:
            if isinstance(item, str) and item.endswith('.gif'):
                if not os.path.isfile(item):
                    pixmap = QPixmap(os.path.dirname(__file__) + '/icons/error.png')
                    self.label.setPixmap(pixmap)
                else:
                    self.movie = QMovie(item)
                    self.movie.setCacheMode(QMovie.CacheAll)
                    self.movie.start()
                    self.movie.stop()
                    self.movie.jumpToFrame(20)
                    self.label.setMovie(self.movie)
                    self.movie.setScaledSize(self.movie.scaledSize())
            else:
                if not os.path.isfile(item):
                    pixmap = QPixmap(os.path.dirname(__file__) + '/icons/error.png')
                else:
                    pixmap = QPixmap(item)
                self.label.setPixmap(pixmap.scaled(self.label.width(), self.label.height(), Qt.KeepAspectRatio))

    def enterEvent(self, event):
        try:
            if not self.drop:
                self.movie.jumpToFrame(0)
                self.movie.start()
        except AttributeError:
            pass

    def leaveEvent(self, event):
        try:
            if not self.drop:
                self.movie.jumpToFrame(20)
                self.movie.stop()
        except AttributeError:
            pass


# --------------------------------------- GIF Conversion -------------------------------------------------------------
class ConvertGif(QRunnable):
    def __init__(self, item, output, pos, frame_length, ffmpeg):
        super(ConvertGif, self).__init__()
        self.ffmpeg = ffmpeg
        self.output = output
        self.start_frame = None
        try:
            if isinstance(item.split('$$'), list):
                self.input, self.start_frame = item.split('$$')
        except Exception:
            self.input = item
        if os.path.splitext(self.input)[1] in ['.exr', '.png', '.jpeg', '.jpg', '.tiff', '.tif'] and \
                (frame_length is None or frame_length.strip() == ''):
            self.output = os.path.splitext(self.output)[0] + '.png'
        self.item = item
        self.conversion_signals = ConversionSignal()
        self.pos = pos

    def run(self):
        try:
            if os.path.isfile(self.output):
                os.remove(self.output)
        except Exception:
            pass
        if not os.path.isfile(self.output):
            if not self.start_frame:
                cmds = [self.ffmpeg, 
                        '-i', self.input, 
                        '-vf', 'scale={}:{}:force_original_aspect_ratio=decrease'.format(DIMENSION_X, DIMENSION_Y),
                        '-r', '24', 
                        self.output, 
                        '-hide_banner']
            else:
                cmds = [self.ffmpeg, 
                        '-start_number', self.start_frame.split('-')[0], 
                        '-i', self.input, 
                        '-vf', 'scale={}:{}:force_original_aspect_ratio=decrease '.format(DIMENSION_X, DIMENSION_Y), 
                        '-r', '24', 
                        self.output, 
                        '-hide_banner']
            process = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            if process.communicate()[0].decode():
                self.conversion_signals.thread_finished.emit((self.item, self.output, self.pos))
        else:
            self.conversion_signals.thread_finished.emit((self.item, self.output, self.pos))


class RemoveCache(QRunnable):
    def __init__(self, item):
        super(RemoveCache, self).__init__()
        self.remove_signals = RemoveSignal()
        self.item = item

    def run(self):
        self.remove_signals.remove_cache_running.emit(self.item)
        try:
            os.remove(self.item)
            self.remove_signals.remove_cache_finished.emit('cache(s) successfully deleted!')
        except Exception:
            self.remove_signals.remove_cache_finished.emit('Cannot remove cache(s), manually delete!')
            pass


class ConversionSignal(QObject):
    thread_started = Signal(str)
    thread_finished = Signal(tuple)


class RemoveSignal(QObject):
    remove_cache_running = Signal(str)
    remove_cache_finished = Signal(str)




