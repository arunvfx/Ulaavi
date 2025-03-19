# -------------------------------- built-in Modules ----------------------------------
import os
from pathlib import Path

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets, QtMultimediaWidgets, QtMultimedia, QtCore, QtGui
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtMultimediaWidgets, QtMultimedia, QtCore, QtGui

# -------------------------------- Custom Modules ------------------------------------
from . import _preview_proxy


class ThumbnailOverlay(QtWidgets.QFrame):
    def __init__(self, width, height, parent=None):
        super().__init__(parent)
        # self.setAlignment(QtCore.Qt.AlignCenter)
        self.setStyleSheet("background: transparent;color: #cacaca;")

        self.overlay_label = QtWidgets.QLabel(self)

        self.__hLayout = QtWidgets.QHBoxLayout(self)
        self.label_left = QtWidgets.QLabel()
        self.label_right = QtWidgets.QLabel()
        self.__hLayout.addWidget(self.label_left)
        self.__hLayout.addWidget(self.label_right)

        self.label_left.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft)
        self.label_right.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight)

        self.__width, self.__height = width, height

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        # self.setContentsMargins(10, 0, 10, 0)

        # Create gradient for half the label
        gradient = QtGui.QLinearGradient(0, self.__width / 2, 0, self.__height)
        gradient.setColorAt(0, QtGui.QColor(60, 60, 60, 150))
        gradient.setColorAt(1, QtGui.QColor(60, 60, 60, 255))

        painter.fillRect(3, self.__height / 1.3, self.__width - 6, self.__height, gradient)
        painter.end()

        self.overlay_label.paintEvent(event)


class Thumbnails(QtWidgets.QFrame):

    def __init__(self,
                 thumbnail_width,
                 thumbnail_height,
                 is_dropped: bool = False,
                 is_input_image: bool = False):
        super().__init__()
        self.__is_input_image = is_input_image

        self.thumbnail_width = thumbnail_width
        self.thumbnail_height = thumbnail_height
        self.__error_image = f'{os.path.dirname(os.path.dirname(__file__))}/icons/error.png'
        self.video = _preview_proxy.ProxyPreview('', self.thumbnail_width, self.thumbnail_height)

        self.setMinimumWidth(thumbnail_width)
        self.setMinimumHeight(thumbnail_height)
        self.__vLayout_main = QtWidgets.QVBoxLayout(self)
        self.__vLayout_main.setContentsMargins(3, 3, 3, 3)

        self.__stacked_widget = QtWidgets.QStackedWidget()

        if is_input_image:
            self.video.progress_bar.hide()

        self.__vLayout_main.addWidget(self.__stacked_widget)
        self.__stacked_widget.addWidget(self.video)

        self.thumbnail_overlay = ThumbnailOverlay(self.thumbnail_width, self.thumbnail_height, self)
        self.thumbnail_overlay.setGeometry(0, 0, self.thumbnail_width, self.thumbnail_height)

        self._set_widget_properties()

        if is_dropped:
            self._preview_conversion_gif()

    def _set_widget_properties(self) -> None:
        self.__stacked_widget.setCurrentIndex(0)
        self.__stacked_widget.setContentsMargins(0, 0, 0, 0)
        self.set_font_size()

    def set_font_size(self, font_size: float = 10):
        font_ = self.thumbnail_overlay.overlay_label.font()
        font_.setPixelSize(font_size)
        self.thumbnail_overlay.label_left.setFont(font_)
        self.thumbnail_overlay.label_right.setFont(font_)

    def set_metadata_overlay(self, metadata: dict, tags: list):
        resolution = ''
        metadata['Tags'] = ','.join(tags) if tags else '-'
        width = metadata.get('width')
        height = metadata.get('height')
        if width and height:
            resolution = f'{width}x{height}'

        length = len(list(metadata))-2
        half_the_length = round(length) / 2

        meta_string_left = f'Resolution: {resolution}'
        meta_string_right = ''

        for index, (key, value) in enumerate(metadata.items()):
            if key in ('width', 'height'):
                continue

            if index < half_the_length:
                meta_string_left += '\n'
                meta_string_left += f'{key}: {value}'

            else:
                meta_string_right += '\n'
                meta_string_right += f'{key}: {value}'

        self.thumbnail_overlay.label_left.setText(meta_string_left)
        self.thumbnail_overlay.label_right.setText(meta_string_right)

    def _preview_conversion_gif(self):
        self.movie = QtGui.QMovie(f"{os.path.dirname(os.path.dirname(__file__))}/icons/processing.gif")
        self.movie.setScaledSize(QtCore.QSize(self.thumbnail_width, self.thumbnail_height))
        self.video.video_label.setMovie(self.movie)
        self.movie.jumpToFrame(0)
        opacity = QtWidgets.QGraphicsOpacityEffect()
        opacity.setOpacity(0.3)
        self.video.video_label.setGraphicsEffect(opacity)
        self.movie.start()

    def update_image_thumbnail(self, image_file) -> None:
        try:
            self.movie.deleteLater()
        except:
            pass

        if os.path.isfile(image_file) is False:
            image_file = self.__error_image

        if os.path.isfile(image_file):
            pixmap = QtGui.QPixmap(image_file)
            self.video.video_label.setPixmap(
                pixmap.scaled(
                    self.thumbnail_width,
                    self.thumbnail_height,
                    QtCore.Qt.KeepAspectRatio)
            )

        self.video.video_label.thumbnail = image_file

    def update_video_thumbnail(self, mov_file) -> None:
        self.video.proxy_file = mov_file

    def enterEvent(self, event):
        """
        play gif if mouse cursor enters the cell.
        """

        try:
            self.thumbnail_overlay.hide()
            if self.__is_input_image:
                return
        except Exception:
            pass

    def leaveEvent(self, event):
        """
        stop gif if mouse cursor leaves the cell.
        """
        try:
            self.thumbnail_overlay.show()

            if self.__is_input_image:
                return

        except Exception:
            pass
