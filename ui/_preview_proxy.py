# -------------------------------- built-in Modules ----------------------------------
import os.path
import sys

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets, QtMultimediaWidgets, QtMultimedia, QtCore, QtGui
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtMultimediaWidgets, QtMultimedia, QtCore, QtGui

# -------------------------------- Custom Modules ------------------------------------
# sys.path.append('C:/Users/arunv/Documents/MyWork/ulaavi/v002/Ulaavi/.venv_/Lib/site-packages')
import cv2


class ProxyPreview(QtWidgets.QWidget):
    def __init__(self, proxy_file, thumbnail_width, thumbnail_height):
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
        self.progress_bar.setFixedHeight(5)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("QProgressBar::chunk{background-color: #232323;}")

        self.__vLayout.addWidget(self.video_label)
        self.__vLayout.addWidget(self.progress_bar)
        self._set_widget_properties()

    def _set_widget_properties(self):
        self.__vLayout.setSpacing(0)
        self.video_label.setContentsMargins(0, 0, 0, 0)
        self.__vLayout.setContentsMargins(0, 0, 0, 0)
        self.progress_bar.setContentsMargins(0, 0, 0, 0)
        self.setGeometry(100, 100, self.thumbnail_width, self.thumbnail_height)

    def eventFilter(self, obj, event):
        if event.type() == event.Type.Enter:
            self.start_video_preview(obj)

        elif event.type() == event.Type.Leave:
            self.stop_video_preview(obj)
            self.progress_bar.setValue(0)

        return super().eventFilter(obj, event)

    def start_video_preview(self, video_label):
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

    def stop_video_preview(self, video_label):
        if hasattr(video_label, 'timer'):
            try:
                video_label.timer.stop()
            except RuntimeError:
                pass
            video_label.timer.deleteLater()

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

    def update_video_frame(self, video_label):
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

        # Create a QImage from the frame
        q_image = QtGui.QImage(frame_rgb.data, width, height, bytes_per_line, QtGui.QImage.Format_RGB888)

        video_label.setPixmap(QtGui.QPixmap.fromImage(q_image))
        self.progress_bar.setValue(self.progress_bar.value() + 1)

    def resize_with_aspect_ratio(self, image, inter=cv2.INTER_AREA):
        """
        Resize an image while maintaining its aspect ratio.

        :param image: Input image (numpy array).
        :param inter: Interpolation method (default is cv2.INTER_AREA).
        :return: Resized image.
        """

        if self.thumbnail_width is None and self.thumbnail_height is None:
            return image

        (image_height, image_width) = image.shape[:2]
        image_aspect_ratio = image_width / image_height
        label_aspect_ratio = self.thumbnail_width / self.thumbnail_height

        if image_aspect_ratio >= label_aspect_ratio:
            # Frame is wider than the label, scale based on width
            new_width = self.thumbnail_width
            new_height = int(new_width / image_aspect_ratio)
        else:
            # Frame is taller than the label, scale based on height
            new_height = self.thumbnail_height
            new_width = int(new_height * image_aspect_ratio)

        resized = cv2.resize(image, (new_width, new_height), interpolation=inter)
        return resized
