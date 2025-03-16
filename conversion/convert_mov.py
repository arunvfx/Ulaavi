import os.path
import re
import subprocess
import json
import time
import datetime
from data import config
from . import _commands

try:
    from PySide2.QtCore import QObject, QRunnable, Signal
except ModuleNotFoundError:
    from PySide6.QtCore import QObject, QRunnable, Signal


def _get_file_metadata(source_file):
    cmds = _commands.extract_video_thumbnail_frame(source_file)
    process = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = process.communicate()

    thumbnail_frame_time = 0
    fps = 24
    total_frames = 1
    width, height = None, None
    if not out:
        return thumbnail_frame_time, fps, total_frames, width, height

    out = json.loads(out)
    if not out:
        return thumbnail_frame_time, fps, total_frames, width, height

    frames = out['streams'][0].get('nb_frames')
    fps = _get_fps(out['streams'][0]['r_frame_rate'])
    total_frames = frames if frames else 1
    width = out['streams'][0].get('width')
    height = out['streams'][0].get('height')
    duration = out['streams'][0].get('duration')
    thumbnail_frame_time = float(duration) // 2 if duration else None

    return thumbnail_frame_time, fps, total_frames, width, height


def _get_fps(frame_rate):
    raw_fps = tuple(map(int, frame_rate.split('/')))
    return raw_fps[0] / raw_fps[1]


def _make_directory(file_path: str):
    path_ = os.path.dirname(file_path)
    if os.path.isdir(path_) is False:
        os.makedirs(path_)


class Signals(QObject):
    on_render_completed = Signal(str, str, dict)
    on_render_error = Signal(str)


class ConvertMov(QRunnable):

    def __init__(self, source_file: str, output_file: str, is_image_seq: bool, thumb_resolutionX: int,
                 thumb_resolutionY: int):
        super().__init__()
        self.signals = Signals()

        self.__source_file = source_file
        self.__output_file = output_file
        self.__is_image_seq = is_image_seq
        self.__thumb_resolutionX = thumb_resolutionX
        self.__thumb_resolutionY = thumb_resolutionY

    def run(self):
        _make_directory(self.__output_file)

        if not self.__is_image_seq and self.__source_file.endswith(config.supported_video_formats):
            thumbnail_frame_time, fps, total_frames, width, height = _get_file_metadata(self.__source_file)
            metadata = {'FPS': float("{:.2f}".format(float(fps))),
                        'Frames': total_frames,
                        'width': width,
                        'height': height}

            self._convert_video(thumbnail_frame_time, fps, metadata)

        elif not self.__is_image_seq and self.__source_file.endswith(config.supported_image_formats):
            thumbnail_frame_time, fps, total_frames, width, height = _get_file_metadata(self.__source_file)
            metadata = {'FPS': float("{:.2f}".format(float(fps))),
                        'Frames': total_frames,
                        'width': width,
                        'height': height}
            self._convert_image(self.__source_file, metadata)

        elif self.__is_image_seq:
            source_file, frame_range = self.__source_file.rsplit(' ', 1)
            start_frame, end_frame = frame_range.split('-')
            thumbnail_frame_time, fps, total_frames, width, height = _get_file_metadata(source_file)
            metadata = {'FPS': float("{:.2f}".format(float(fps))),
                        'Frames': end_frame,
                        'width': width,
                        'height': height}

            self._convert_image_sequence(source_file, thumbnail_frame_time, fps, start_frame, metadata)

    def _convert_video(self, thumbnail_frame_time, fps, metadata) -> None:
        """
        convert video to mov

        :param thumbnail_frame_time: time in which sec to take thumbnail image
        :type thumbnail_frame_time: float
        :param metadata: video metadata
        :type metadata: dict
        :return: None
        :rtype: None
        """
        thumbnail_image = f'{os.path.splitext(self.__output_file)[0]}.png'

        if not os.path.isfile(self.__output_file):
            command = _commands.convert_video(
                self.__source_file, self.__output_file, self.__thumb_resolutionX, self.__thumb_resolutionY, fps)

            if not self._execute_render_command(command):
                return

        if self._generate_thumbnail(thumbnail_frame_time, thumbnail_image, self.__source_file):
            self.signals.on_render_completed.emit(self.__output_file, thumbnail_image, metadata)

    def _convert_image_sequence(self, source_file, thumbnail_frame_time, fps, start_frame, metadata):

        thumbnail_image = f'{os.path.splitext(self.__output_file)[0]}.png'

        if not os.path.isfile(self.__output_file):
            command = _commands.convert_image_sequence(
                source_file, self.__output_file, self.__thumb_resolutionX, self.__thumb_resolutionY, start_frame,
                fps)

            if not self._execute_render_command(command):
                return

        thumbnail_image1 = f'_$$$${datetime.datetime.now().strftime("%M_%S_%f")}_'.join(re.split(r"%\d{2}d", thumbnail_image))
        if self._generate_thumbnail(thumbnail_frame_time, thumbnail_image1, source_file):
            os.rename(thumbnail_image1, thumbnail_image)
            self.signals.on_render_completed.emit(self.__output_file, thumbnail_image, metadata)

    def _convert_image(self, source_file, metadata):
        thumbnail_image = f'{os.path.splitext(self.__output_file)[0]}.png'
        if not os.path.isfile(self.__output_file):
            command = _commands.convert_image(
                source_file, self.__output_file, self.__thumb_resolutionX, self.__thumb_resolutionY)

            if not self._execute_render_command(command):
                return

        self.signals.on_render_completed.emit(self.__output_file, thumbnail_image, metadata)

    def _execute_render_command(self, command: list) -> bool:
        """
        execute render

        :param command: command to execute
        :type command: list
        :return: is rendered or not
        :rtype: bool
        """
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, error = process.communicate()

        if error and not out:
            self.signals.on_render_error.emit(str(error.decode()))
            return False

        return True

    def _generate_thumbnail(self, thumbnail_frame_time, thumbnail_image, input_file):

        command = _commands.extract_image_from_video(input_file,
                                                     thumbnail_image,
                                                     self.__thumb_resolutionX,
                                                     self.__thumb_resolutionY,
                                                     thumbnail_frame_time)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, error = process.communicate()

        if error:
            self.signals.on_render_error.emit(str(error.decode()))
            return False
        time.sleep(0.5)
        return True
