"""
This module provides a ProxyPreview widget for previewing video files with a progress bar. The widget displays a video
preview when the mouse hovers over it and shows a progress bar indicating the current playback position.
It supports resizing the video while maintaining its aspect ratio.

Key Features:
    Video Preview: Displays a video preview when the mouse hovers over the widget.
    Progress Bar: Shows a progress bar indicating the current playback position.
    Aspect Ratio Maintenance: Resizes the video while maintaining its aspect ratio.
    Dynamic Frame Update: Updates the video frame dynamically during playback.

Dependencies:
    Built-in Modules: os
    Third-Party Modules:
        PySide2 or PySide6 for GUI components.
        cv2 (OpenCV) for video processing.

Classes:
    ProxyPreview: A custom widget for video preview and playback control.

Attributes:
    thumbnail_width (int): The width of the video preview.
    thumbnail_height (int): The height of the video preview.
    proxy_file (str): The path to the video file.
    __total_frames (int): The total number of frames in the video.

Methods:
    __init__: Initializes the ProxyPreview widget.
    _set_widget_properties: Configures widget properties, such as layout margins and geometry.
    eventFilter: Handles mouse enter and leave events to start/stop video preview.
    start_video_preview: Starts the video preview when the mouse enters the widget.
    stop_video_preview: Stops the video preview when the mouse leaves the widget.
    update_video_frame: Updates the video frame displayed in the label.
    resize_with_aspect_ratio: Resizes an image while maintaining its aspect ratio.
"""


# -------------------------------- built-in Modules ----------------------------------
import os

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets, QtMultimediaWidgets, QtMultimedia, QtCore, QtGui
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtMultimediaWidgets, QtMultimedia, QtCore, QtGui

# -------------------------------- Custom Modules ------------------------------------
import cv2


class ProxyPreview(QtWidgets.QWidget):
    """
    A widget for previewing video files with a progress bar.

    This widget displays a video preview when the mouse hovers over it and shows a progress bar
    indicating the current playback position. It supports resizing the video while maintaining
    its aspect ratio.

    Attributes:
        thumbnail_width (int): The width of the video preview.
        thumbnail_height (int): The height of the video preview.
        proxy_file (str): The path to the video file.
        __total_frames (int): The total number of frames in the video.
    """

    def __init__(self, proxy_file: str, thumbnail_width: int, thumbnail_height: int) -> None:
        """
        Initialize the ProxyPreview widget.

        :param proxy_file: Path to the video file.
        :type proxy_file: str
        :param thumbnail_width: Width of the video preview.
        :type thumbnail_width: int
        :param thumbnail_height: Height of the video preview.
        :type thumbnail_height: int
        """
        super().__init__()
        self.thumbnail_width = thumbnail_width
        self.thumbnail_height = thumbnail_height
        self.__total_frames = 0

        self.proxy_file = proxy_file

        self.__vLayout = QtWidgets.QVBoxLayout(self)
        self.video_label = QtWidgets.QLabel()
        self.video_label.installEventFilter(self)
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(3)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("QProgressBar::chunk{background-color: #232323;} "
                                        "QProgressBar{border: 0; background-color: transparent;}")

        self.__vLayout.addWidget(self.video_label)
        self.__vLayout.addWidget(self.progress_bar)
        self._set_widget_properties()

    def _set_widget_properties(self) -> None:
        """
        Configure widget properties, such as layout margins and geometry.
        """
        self.__vLayout.setSpacing(0)
        self.video_label.setContentsMargins(0, 0, 0, 0)
        self.__vLayout.setContentsMargins(0, 0, 0, 0)
        self.progress_bar.setContentsMargins(0, 0, 0, 0)
        self.setGeometry(0, 0, self.thumbnail_width, self.thumbnail_height)

    def eventFilter(self, obj: QtWidgets.QWidget, event: QtCore.QEvent) -> bool:
        """
        Handle mouse enter and leave events to start/stop video preview.

        :param obj: The object that triggered the event.
        :type obj: QtWidgets.QWidget
        :param event: The event object.
        :type event: QtCore.QEvent
        :return: True if the event is handled, otherwise False.
        :rtype: bool
        """
        if event.type() == event.Type.Enter:
            self.start_video_preview(obj)

        elif event.type() == event.Type.Leave:
            self.stop_video_preview(obj)
            self.progress_bar.setValue(0)

        return super().eventFilter(obj, event)

    def start_video_preview(self, video_label: QtWidgets.QLabel) -> None:
        """
        Start the video preview when the mouse enters the widget.

        :param video_label: The label used to display the video.
        :type video_label: QtWidgets.QLabel
        """
        if not self.proxy_file or not os.path.isfile(self.proxy_file):
            return

        video_label.cap = cv2.VideoCapture(self.proxy_file)
        if not video_label.cap.isOpened():
            return

        self.__total_frames = int(video_label.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = video_label.cap.get(cv2.CAP_PROP_FPS)
        self.progress_bar.setRange(0, self.__total_frames)
        video_label.timer = QtCore.QTimer()
        video_label.timer.timeout.connect(lambda: self.update_video_frame(video_label))
        video_label.timer.start(round(1000 / fps))

    def stop_video_preview(self, video_label: QtWidgets.QLabel) -> None:
        """
        Stop the video preview when the mouse leaves the widget.

        :param video_label: The label used to display the video.
        :type video_label: QtWidgets.QLabel
        """
        if hasattr(video_label, 'timer'):
            try:
                video_label.timer.stop()
                video_label.timer.deleteLater()
            except RuntimeError:
                pass

        if hasattr(video_label, 'cap'):
            video_label.cap.release()

        if hasattr(video_label, 'thumbnail'):
            pixmap = QtGui.QPixmap(video_label.thumbnail)
            self.video_label.setPixmap(
                pixmap.scaled(
                    self.thumbnail_width,
                    self.thumbnail_height,
                    QtCore.Qt.KeepAspectRatio)
            )

    def update_video_frame(self, video_label: QtWidgets.QLabel) -> None:
        """
        Update the video frame displayed in the label.

        :param video_label: The label used to display the video.
        :type video_label: QtWidgets.QLabel
        """
        if self.progress_bar.value() == self.__total_frames:
            self.progress_bar.setValue(0)

        ret, frame = video_label.cap.read()

        if not ret:
            video_label.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = video_label.cap.read()
            if not ret:
                return

        frame = self.resize_with_aspect_ratio(frame)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channels = frame_rgb.shape
        bytes_per_line = channels * width

        q_image = QtGui.QImage(frame_rgb.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)
        video_label.setPixmap(QtGui.QPixmap.fromImage(q_image))
        self.progress_bar.setValue(self.progress_bar.value() + 1)

    def resize_with_aspect_ratio(self, image, inter=cv2.INTER_AREA):
        """
        Resize an image while maintaining its aspect ratio.

        :param image: Input image (numpy array).
        :type image: numpy.ndarray
        :param inter: Interpolation method (default is cv2.INTER_AREA).
        :type inter: int
        :return: Resized image.
        :rtype: numpy.ndarray
        """

        if self.thumbnail_width is None and self.thumbnail_height is None:
            return image

        image_height, image_width = image.shape[:2]
        image_aspect_ratio = image_width / image_height
        label_aspect_ratio = self.thumbnail_width / self.thumbnail_height

        if image_aspect_ratio >= label_aspect_ratio:
            # image is wider than the video_label, scale based on width
            new_width = self.thumbnail_width
            new_height = int(new_width / image_aspect_ratio)
        else:
            # image is taller than the video_label, scale based on height
            new_height = self.thumbnail_height
            new_width = int(new_height * image_aspect_ratio)

        return cv2.resize(image, (new_width, new_height), interpolation=inter)
