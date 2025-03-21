"""
Thumbnail Display Module

This module provides custom Qt widgets for displaying and managing thumbnails of images and videos.
It includes features such as metadata overlays, dynamic thumbnail updates, and visual indicators for processing states.

Key Features:
- **ThumbnailOverlay**: A transparent overlay for displaying metadata (e.g., resolution, tags) on thumbnails.
- **Thumbnails**: A widget for rendering image and video thumbnails with support for dynamic updates and processing animations.
- **Metadata Display**: Supports displaying metadata in a structured format on the thumbnail overlay.
- **Error Handling**: Automatically displays an error image if the thumbnail file is missing or invalid.
- **Processing Animation**: Shows a GIF animation to indicate ongoing processing or conversion.

Usage:
------
- Use `Thumbnails` to create and manage thumbnails for images or videos.
- Customize the overlay with metadata using `set_metadata_overlay`.
- Update thumbnails dynamically with `update_image_thumbnail` or `update_video_thumbnail`.
"""

# -------------------------------- built-in Modules ----------------------------------
import os
from typing import List

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets, QtMultimediaWidgets, QtMultimedia, QtCore, QtGui
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtMultimediaWidgets, QtMultimedia, QtCore, QtGui

# -------------------------------- Custom Modules ------------------------------------
from . import _preview_proxy


class ThumbnailOverlay(QtWidgets.QFrame):
    """
    A custom QFrame widget that provides an overlay for thumbnails.
    This overlay includes a gradient background and labels for displaying metadata.
    """

    def __init__(self, width, height, parent=None):
        """
        Initialize attributes

        param width: The width of the overlay.
        :type width: int
        :param height: The height of the overlay.
        :type height: int
        :param parent: The parent widget, defaults to None.
        :type parent: QWidget, optional
        """
        super().__init__(parent)
        self.setStyleSheet("background: transparent;color: #cacaca;")
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setFrameShadow(QtWidgets.QFrame.Plain)

        self.overlay_label = QtWidgets.QLabel(self)

        self.__hLayout = QtWidgets.QHBoxLayout(self)
        self.label_left = QtWidgets.QLabel()
        self.label_right = QtWidgets.QLabel()
        self.__hLayout.addWidget(self.label_left)
        self.__hLayout.addWidget(self.label_right)

        self.label_left.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft)
        self.label_right.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignRight)

        self.__width, self.__height = width, height

    def paintEvent(self, event: QtCore.QEvent) -> None:
        """
        Overrides the paint event to draw a gradient background.

        :param event: The paint event.
        :type event: QPaintEvent
        """
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        gradient = QtGui.QLinearGradient(0, self.__width / 2, 0, self.__height)
        gradient.setColorAt(0, QtGui.QColor(60, 60, 60, 150))
        gradient.setColorAt(1, QtGui.QColor(60, 60, 60, 255))

        painter.fillRect(3, self.__height / 1.3, self.__width - 6, self.__height, gradient)
        painter.end()

        self.overlay_label.paintEvent(event)


class Thumbnails(QtWidgets.QFrame):
    """
    A custom QFrame widget for displaying thumbnails of images or videos.
    """

    def __init__(self,
                 thumbnail_width: int,
                 thumbnail_height: int,
                 is_dropped: bool = False,
                 is_input_image: bool = False):
        """
        Initialize attributes

        :param thumbnail_width: The width of the thumbnail.
        :type thumbnail_width: int
        :param thumbnail_height: The height of the thumbnail.
        :type thumbnail_height: int
        :param is_dropped: Indicates if the thumbnail is for a dropped item, defaults to False.
        :type is_dropped: bool, optional
        :param is_input_image: Indicates if the thumbnail is for an input image, defaults to False.
        :type is_input_image: bool, optional
        """
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
        """
        Sets the initial properties of the widget, such as layout margins and font size.
        """
        self.__stacked_widget.setCurrentIndex(0)
        self.__stacked_widget.setContentsMargins(0, 0, 0, 0)
        self.set_font_size()

    def set_font_size(self, font_size: float = 10) -> None:
        """
        Sets the font size for the overlay labels.

        :param font_size: The font size to set, defaults to 10.
        :type font_size: float, optional
        """
        font_ = self.thumbnail_overlay.overlay_label.font()
        font_.setPixelSize(font_size)
        self.thumbnail_overlay.label_left.setFont(font_)
        self.thumbnail_overlay.label_right.setFont(font_)

    def set_metadata_overlay(self, metadata: dict, tags: List[str]) -> None:
        """
        Sets the metadata and tags to be displayed in the overlay.

        :param metadata: A dictionary containing metadata information.
        :type metadata: dict
        :param tags: A list of tags associated with the thumbnail.
        :type tags: list[str]
        """
        resolution = ''
        metadata['Tags'] = ','.join(tags) if tags else '-'
        width = metadata.get('width')
        height = metadata.get('height')
        if width and height:
            resolution = f'{width}x{height}'

        length = len(list(metadata)) - 2
        half_the_length = round(length) * 0.5

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

    def _preview_conversion_gif(self) -> None:
        """
        Displays a processing GIF animation to indicate ongoing conversion.
        """
        self.movie = QtGui.QMovie(f"{os.path.dirname(os.path.dirname(__file__))}/icons/processing.gif")
        self.movie.setScaledSize(QtCore.QSize(self.thumbnail_width, self.thumbnail_height))
        self.video.video_label.setMovie(self.movie)
        self.movie.jumpToFrame(0)
        opacity = QtWidgets.QGraphicsOpacityEffect()
        opacity.setOpacity(0.3)
        self.video.video_label.setGraphicsEffect(opacity)
        self.movie.start()

    def update_image_thumbnail(self, image_file: str) -> None:
        """
       Updates the thumbnail with the provided image file.

       :param image_file: The path to the image file.
       :type image_file: str
       """
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
        """
        Updates the thumbnail with the provided video file.

        :param mov_file: The path to the video file.
        :type mov_file: str
        """
        self.video.proxy_file = mov_file

    def enterEvent(self, event: QtCore.QEvent) -> None:
        """
        Hides the overlay when the mouse cursor enters the widget.

        :param event: The enter event.
        :type event: QEvent
        """

        try:
            self.thumbnail_overlay.hide()
            if self.__is_input_image:
                return
        except Exception:
            pass

    def leaveEvent(self, event: QtCore.QEvent) -> None:
        """
        Shows the overlay when the mouse cursor leaves the widget.

        :param event: The leave event.
        :type event: QEvent
        """
        try:
            self.thumbnail_overlay.show()

            if self.__is_input_image:
                return

        except Exception:
            pass
