# -------------------------------- built-in Modules ----------------------------------
import os
from pathlib import Path

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets, QtMultimediaWidgets, QtMultimedia, QtCore, QtGui
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtMultimediaWidgets, QtMultimedia, QtCore, QtGui


# -------------------------------- Custom Modules ------------------------------------


class GradientLabel(QtWidgets.QLabel):
    def __init__(self, width, height, parent=None):
        super().__init__(parent)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setStyleSheet("background: transparent;color: #cacaca;")  # Ensure transparency

        self.setAlignment(QtCore.Qt.AlignBottom | QtCore.Qt.AlignLeft)  # Align to bottom and center
        self.__width, self.__height = width, height

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setContentsMargins(10, 0, 10, 0)

        # Create gradient for half the label
        gradient = QtGui.QLinearGradient(0, self.__width / 2, 0, self.__height)
        gradient.setColorAt(0, QtGui.QColor(60, 60, 60, 150))  # Semi-transparent red
        gradient.setColorAt(1, QtGui.QColor(60, 60, 60, 255))  # Semi-transparent blue

        painter.fillRect(3, self.__height / 1.3, self.__width-6, self.__height, gradient)  # Fill left half
        painter.end()

        # Call the base class paint event
        super().paintEvent(event)


class Thumbnails(QtWidgets.QFrame):

    def __init__(self,
                 thumbnail_width,
                 thumbnail_height,
                 is_dropped: bool = False,
                 is_input_image: bool = False):
        super().__init__()
        self.__is_input_image = is_input_image

        self.preview_thumb = ''
        self.font_size = 8
        self.thumbnail_width = thumbnail_width
        self.thumbnail_height = thumbnail_height
        self.__is_dropped = is_dropped
        self.__error_image = f'{os.path.dirname(os.path.dirname(__file__))}/icons/error.png'
        self.__root_path = os.path.dirname(os.path.dirname(__file__))

        self.setMinimumWidth(thumbnail_width)
        self.setMinimumHeight(thumbnail_height)
        self.__vLayout_main = QtWidgets.QVBoxLayout(self)
        self.__vLayout_main.setContentsMargins(3, 3, 3, 3)

        self.__stacked_widget = QtWidgets.QStackedWidget()

        self.__image_frame = QtWidgets.QFrame()
        self.__stack_one_vLayout = QtWidgets.QVBoxLayout(self.__image_frame)
        self.__image_label = QtWidgets.QLabel()
        self.__image_label.setGeometry(0, 0, self.thumbnail_width, self.thumbnail_height)
        self.__stack_one_vLayout.addWidget(self.__image_label)
        self.__stacked_widget.addWidget(self.__image_frame)

        if not is_input_image:
            self.__video_frame = QtWidgets.QFrame()
            self.__stack_two_vLayout = QtWidgets.QVBoxLayout(self.__video_frame)
            self.__slider = QtWidgets.QProgressBar()

            self.media_player = QtMultimedia.QMediaPlayer()
            video_widget = QtMultimediaWidgets.QVideoWidget()
            self.media_player.setVideoOutput(video_widget)
            video_widget.setGeometry(0, 0, self.thumbnail_width, self.thumbnail_height)

            self.__stack_two_vLayout.addWidget(video_widget)
            self.__stack_two_vLayout.addWidget(self.__slider)

            self.__stacked_widget.addWidget(self.__video_frame)

        self.__vLayout_main.addWidget(self.__stacked_widget)

        self.__overlay_label = GradientLabel(self.thumbnail_width, self.thumbnail_height, self)
        self.__overlay_label.setGeometry(0, 0, self.thumbnail_width, self.thumbnail_height)

        self._set_widget_properties()
        self._image_thumbnail()
        self.set_font_size()

    def set_font_size(self, font_size: float = 10):
        font_ = self.__overlay_label.font()
        font_.setPixelSize(font_size)
        self.__overlay_label.setFont(font_)

    def set_label(self, label: dict):
        resolution = ''

        width = label.get('width')
        height = label.get('height')
        if width and height:
            resolution = f'{width}x{height}'

        meta_string = f'Resolution: {resolution}\n'
        for key, value in label.items():
            if key in ('width', 'height'):
                continue
            meta_string += key
            meta_string += f':{value}\n'

        self.__overlay_label.setText(meta_string)

    def _set_widget_properties(self) -> None:
        self.__stacked_widget.setCurrentIndex(0)
        self.__stacked_widget.setContentsMargins(0, 0, 0, 0)
        self.__stack_one_vLayout.setSpacing(0)
        self.__stack_one_vLayout.setContentsMargins(0, 0, 0, 0)

        if not self.__is_input_image:
            self.__stack_two_vLayout.setContentsMargins(0, 0, 0, 0)
            self.__stack_two_vLayout.setSpacing(0)

        try:
            self.media_player.positionChanged.connect(self.positionChanged)
            self.media_player.durationChanged.connect(self.durationChanged)

            self.media_player.setNotifyInterval(100)
            self.media_player.setMuted(True)
            # self.__slider.setOrientation(QtCore.Qt.Horizontal)
            self.__slider.setValue(0)
            self.__slider.setMaximumHeight(5)
            self.__slider.setTextVisible(False)

            self.__slider.setStyleSheet("QProgressBar::chunk{background-color: #232323;}")
        except Exception:
            pass

    def _image_thumbnail(self):

        if self.__is_dropped:
            self._preview_conversion_gif()

    def _preview_conversion_gif(self):
        self.movie = QtGui.QMovie(f"{self.__root_path}/icons/processing.gif")
        self.movie.setScaledSize(QtCore.QSize(self.thumbnail_width, self.thumbnail_height))
        self.__image_label.setMovie(self.movie)
        self.movie.jumpToFrame(0)
        opacity = QtWidgets.QGraphicsOpacityEffect()
        opacity.setOpacity(0.3)
        self.__image_label.setGraphicsEffect(opacity)
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
            self.__image_label.setPixmap(
                pixmap.scaled(
                    self.thumbnail_width,
                    self.thumbnail_height,
                    QtCore.Qt.KeepAspectRatio)
            )

    def update_video_thumbnail(self, mov_file) -> None:
        self.media_player.setMedia(QtCore.QUrl.fromLocalFile(mov_file))

    def enterEvent(self, event):
        """
        play gif if mouse cursor enters the cell.
        """

        try:
            self.__overlay_label.hide()
            if self.__is_input_image:
                return

            self.__stacked_widget.setCurrentIndex(1)
            self.media_player.play()
        except Exception:
            pass

    def leaveEvent(self, event):
        """
        stop gif if mouse cursor leaves the cell.
        """
        try:
            self.__overlay_label.show()

            if self.__is_input_image:
                return
            self.media_player.pause()
            self.__stacked_widget.setCurrentIndex(0)

        except Exception:
            pass

    def positionChanged(self, position):
        if position == self.media_player.duration():
            self.media_player.setPosition(0)
            self.media_player.play()
        self.__slider.setValue(position)

    def durationChanged(self, duration):
        pass
        self.__slider.setRange(0, duration)

    def setPosition(self, position):
        self.media_player.setPosition(position)
