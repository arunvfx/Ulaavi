# -------------------------------- built-in Modules ----------------------------------
import os

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets, QtMultimediaWidgets, QtMultimedia, QtCore, QtGui
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtMultimediaWidgets, QtMultimedia, QtCore, QtGui

# -------------------------------- Custom Modules ------------------------------------


class Thumbnails(QtWidgets.QWidget):

    def __init__(self, source_file: str,
                 thumbnail_width,
                 thumbnail_height,
                 is_dropped: bool = False):
        super().__init__()

        self.source_file = source_file
        self.preview_thumb = ''
        self.__is_dropped = is_dropped
        self.thumbnail_width = thumbnail_width
        self.thumbnail_height = thumbnail_height
        self.__root_path = os.path.dirname(os.path.dirname(__file__))
        self.__main_widget = QtWidgets.QWidget()
        self.__main_layout = QtWidgets.QVBoxLayout(self)
        self.__stacked_layout = QtWidgets.QStackedLayout(self.__main_widget)
        self.__thumbnail_image_widget = QtWidgets.QWidget()
        self.__slider = QtWidgets.QProgressBar()
        self.__text_label = QtWidgets.QLabel()
        self.__stacked_layout.addWidget(self.__thumbnail_image_widget)
        self._set_widget_properties()
        self.__main_layout.addWidget(self.__main_widget)
        self.__main_layout.addWidget(self.__text_label)
        self.setLayout(self.__main_layout)

        self._image_thumbnail()

    def set_label(self, label: str):
        self.__text_label.setText(label)

    def _set_widget_properties(self) -> None:
        self.__stacked_layout.setCurrentIndex(0)
        self.__stacked_layout.setContentsMargins(0, 0, 0, 0)

        self.__text_label.setAlignment(QtCore.Qt.AlignHCenter)
        self.__text_label.setFixedHeight(20)

        try:
            self.media_player.positionChanged.connect(self.positionChanged)
            self.media_player.durationChanged.connect(self.durationChanged)

            self.media_player.setNotifyInterval(100)
            self.media_player.setMuted(True)
            self.__slider.setOrientation(QtCore.Qt.Horizontal)
            self.__slider.setValue(0)
            self.__slider.setMaximumHeight(5)
            self.__slider.setTextVisible(False)

            self.__slider.setStyleSheet("QSlider::groove:horizontal {background-color:#232323;}"
                            "QSlider::handle:horizontal {background-color:#434343; height:4px; width: 16px;}");
        except Exception:
            pass

    def _image_thumbnail(self):
        image_layout = QtWidgets.QVBoxLayout(self.__thumbnail_image_widget)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.setSpacing(0)

        self.__image_label = QtWidgets.QLabel()
        self.__image_label.setGeometry(0, 0, self.thumbnail_width, self.thumbnail_height)

        image_layout.addWidget(self.__image_label)

        if self.__is_dropped:
            self._preview_conversion_gif()

    def _preview_conversion_gif(self):
        self.movie = QtGui.QMovie(f"{self.__root_path}/icons/processing.gif")
        self.movie.setScaledSize(self.__image_label.size())
        self.movie.setCacheMode(QtGui.QMovie.CacheAll)
        self.__image_label.setMovie(self.movie)
        self.movie.jumpToFrame(0)
        opacity = QtWidgets.QGraphicsOpacityEffect()
        opacity.setOpacity(0.3)
        self.__image_label.setGraphicsEffect(opacity)
        self.movie.start()

    def _video_thumbnail(self):
        video_layout = QtWidgets.QVBoxLayout(self.__thumbnail_video_widget)
        video_layout.setSpacing(0)
        video_layout.setContentsMargins(0, 0, 0, 0)

        self.media_player = QtMultimedia.QMediaPlayer(None, QtMultimedia.QMediaPlayer.VideoSurface)
        video_widget = QtMultimediaWidgets.QVideoWidget()

        self.media_player.setVideoOutput(video_widget)
        video_widget.setGeometry(0, 0, self.thumbnail_width, self.thumbnail_height)

        video_layout.addWidget(video_widget)
        video_layout.addWidget(self.__slider)

    def update_image_thumbnail(self, image_file) -> None:

        if os.path.isfile(image_file):
            pixmap = QtGui.QPixmap(image_file)
            self.__image_label.setPixmap(
                pixmap.scaled(
                    self.thumbnail_width,
                    self.thumbnail_height,
                    QtCore.Qt.KeepAspectRatio)
            )

    def update_video_thumbnail(self, mov_file) -> None:
        try:
            self.__image_label.deleteLater()
        except:
            pass

        self.__thumbnail_video_widget = QtWidgets.QWidget()
        self.__thumbnail_video_widget.setObjectName('VideoWidget')
        self._video_thumbnail()
        self.__stacked_layout.addWidget(self.__thumbnail_video_widget)

        self.media_player.setMedia(
            QtMultimedia.QMediaContent(QtCore.QUrl.fromLocalFile(mov_file)))

    def enterEvent(self, event):
        """
        play gif if mouse cursor enters the cell.
        """

        try:
            t = self.media_player
            self.__stacked_layout.setCurrentIndex(1)
            self.media_player.play()

        except Exception:
            pass

    def leaveEvent(self, event):
        """
        stop gif if mouse cursor leaves the cell.
        """
        try:
            self.__stacked_layout.setCurrentIndex(0)
            self.media_player.pause()

        except Exception:
            pass

    def positionChanged(self, position):
        if position == self.media_player.duration():
            self.media_player.setPosition(0)
            self.media_player.play()
        self.__slider.setValue(position)

    def durationChanged(self, duration):
        self.__slider.setRange(0, duration)

    def setPosition(self, position):
        print(f'New slider position {position}')
        self.media_player.setPosition(position)
        print(f'Media player updated position {self.media_player.position()}')
