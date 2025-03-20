"""
Summary:

This module provides a QRunnable class, ConvertMov, for converting media files (videos, images, and image sequences)
to .mov format. It also generates thumbnails for the converted media. The module uses ffmpeg commands for media
processing and PySide2/PySide6 for signal handling in a multithreaded environment.
"""

# -------------------------------- built-in Modules ----------------------------------
import os
import re
import subprocess
import json
import time
import datetime
from pathlib import Path

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2.QtCore import QObject, QRunnable, Signal
except ModuleNotFoundError:
    from PySide6.QtCore import QObject, QRunnable, Signal, Slot

# -------------------------------- Custom Modules ------------------------------------
from data import config
from . import _commands
import _utilities


def _get_file_metadata(source_file: str) -> tuple:
    """
    Get metadata for a given image or video file.

    :param source_file: Path to the source file.
    :type source_file: str
    :return: Tuple containing thumbnail frame time, FPS, total frames, width, and height.
    :rtype: tuple[float, float, int, int, int]
    """
    cmds = _commands.extract_video_thumbnail_frame(source_file)
    process = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, _ = process.communicate()

    if not out:
        return 0, 24, 1, None, None

    out = json.loads(out)
    if not out:
        return 0, 24, 1, None, None

    stream = out['streams'][0]
    frames = stream.get('nb_frames', 1)
    fps = _get_fps(stream['r_frame_rate'])
    width = stream.get('width')
    height = stream.get('height')
    duration = stream.get('duration')
    thumbnail_frame_time = float(duration) // 2 if duration else 0

    return thumbnail_frame_time, fps, frames, width, height


def _get_fps(frame_rate) -> float:
    """
    Calculate FPS from a frame rate string.

    :param frame_rate: Frame rate in the format "numerator/denominator".
    :type frame_rate: str
    :return: Calculated FPS.
    :rtype: float
    """
    raw_fps = tuple(map(int, frame_rate.split('/')))
    return raw_fps[0] / raw_fps[1]


class Signals(QObject):
    """
    Custom signals for the ConvertMov class.
    """
    on_render_completed = Signal(str, str, dict)
    on_render_error = Signal(str)


class ConvertMov(QRunnable):
    """
    A QRunnable class for converting media files to .mov format.
    """

    def __init__(self, source_file: str, output_file: str, is_image_seq: bool, thumb_resolutionX: int,
                 thumb_resolutionY: int):

        """
        Initialize the ConvertMov instance.

        :param source_file: Path to the source file.
        :type source_file: str
        :param output_file: Path to the output file.
        :type output_file: str
        :param is_image_seq: Whether the source is an image sequence.
        :type is_image_seq: bool
        :param thumb_resolutionX: Thumbnail width.
        :type thumb_resolutionX: int
        :param thumb_resolutionY: Thumbnail height.
        :type thumb_resolutionY: int
        """
        super().__init__()
        self.signals = Signals()

        self.__source_file = source_file
        self.__output_file = output_file
        self.__is_image_seq = is_image_seq
        self.__thumb_resolutionX = thumb_resolutionX
        self.__thumb_resolutionY = thumb_resolutionY

    def run(self):
        """
        Execute the conversion process.
        """
        _utilities.make_directory(self.__output_file)

        if self.is_image_seq:
            self._process_image_sequence()

        elif self.__source_file.endswith(config.supported_image_formats):
            self._process_image()

        elif self.__source_file.endswith(config.supported_video_formats):
            self._process_video()

    def _process_video(self):
        """
        Process a video file for conversion.
        """
        thumbnail_frame_time, fps, total_frames, width, height = _get_file_metadata(self.__source_file)
        metadata = {'FPS': float("{:.2f}".format(float(fps))),
                    'Frame(s)': total_frames,
                    'width': width,
                    'height': height,
                    'Format': Path(self.__source_file).suffix}

        self._convert_video(thumbnail_frame_time, fps, metadata)

    def _process_image(self):
        """
        Process an image file for conversion.
        """
        thumbnail_frame_time, fps, total_frames, width, height = _get_file_metadata(self.__source_file)
        metadata = {'FPS': float("{:.2f}".format(float(fps))),
                    'Frame(s)': total_frames,
                    'width': width,
                    'height': height,
                    'Format': Path(self.__source_file).suffix}
        self._convert_image(self.__source_file, metadata)

    def _process_image_sequence(self):
        """
        Process an image sequence for conversion.
        """
        source_file, frame_range = self.__source_file.rsplit(' ', 1)
        start_frame, end_frame = frame_range.split('-')
        thumbnail_frame_time, fps, total_frames, width, height = _get_file_metadata(source_file)

        metadata = {'FPS': float("{:.2f}".format(float(fps))),
                    'Frame(s)': str(int(end_frame) - int(start_frame) + 1),
                    'width': width,
                    'height': height,
                    'Format': Path(self.__source_file.rsplit(' ', 1)[0]).suffix}

        self._convert_image_sequence(source_file, thumbnail_frame_time, fps, start_frame, metadata)

    def _convert_video(self, thumbnail_frame_time, fps, metadata) -> None:
        """
        Convert a video file to .mov format.

        :param thumbnail_frame_time: Time to extract the thumbnail frame.
        :type thumbnail_frame_time: float
        :param fps: Frames per second of the video.
        :type fps: float
        :param metadata: Video metadata.
        :type metadata: dict
        """
        thumbnail_image = f'{os.path.splitext(self.__output_file)[0]}.png'

        if not os.path.isfile(self.__output_file):
            command = _commands.convert_video(
                self.__source_file, self.__output_file, self.__thumb_resolutionX, self.__thumb_resolutionY, fps)

            if not self._execute_render_command(command):
                return

        if self._generate_thumbnail(thumbnail_frame_time, thumbnail_image, self.__source_file):
            self.signals.on_render_completed.emit(self.__output_file, thumbnail_image, metadata)

    def _convert_image_sequence(self,
                                source_file: str,
                                thumbnail_frame_time: float,
                                fps: float,
                                start_frame: str,
                                metadata: dict) -> None:
        """
        Convert an image sequence to .mov format.

        :param source_file: Path to the source image sequence.
        :type source_file: str
        :param thumbnail_frame_time: Time to extract the thumbnail frame.
        :type thumbnail_frame_time: float
        :param fps: Frames per second of the sequence.
        :type fps: float
        :param start_frame: Starting frame of the sequence.
        :type start_frame: str
        :param metadata: Sequence metadata.
        :type metadata: dict
        """

        thumbnail_image = f'{os.path.splitext(self.__output_file)[0]}.png'

        if not os.path.isfile(self.__output_file):
            command = _commands.convert_image_sequence(
                source_file, self.__output_file, self.__thumb_resolutionX, self.__thumb_resolutionY, start_frame,
                fps)

            if not self._execute_render_command(command):
                return

        thumbnail_image_temp = f'_$$$${datetime.datetime.now().strftime("%M_%S_%f")}_'.join(
            re.split(r"%\d{2}d", thumbnail_image))

        if self._generate_thumbnail(thumbnail_frame_time, thumbnail_image_temp, source_file):
            os.rename(thumbnail_image_temp, thumbnail_image)
            self.signals.on_render_completed.emit(self.__output_file, thumbnail_image, metadata)

    def _convert_image(self, source_file: str, metadata: dict) -> None:
        """
        Convert an image file to .png format.

        :param source_file: Path to the source image.
        :type source_file: str
        :param metadata: Image metadata.
        :type metadata: dict
        """
        thumbnail_image = f'{os.path.splitext(self.__output_file)[0]}.png'
        if not os.path.isfile(self.__output_file):
            command = _commands.convert_image(
                source_file, self.__output_file, self.__thumb_resolutionX, self.__thumb_resolutionY)

            if not self._execute_render_command(command):
                return

        self.signals.on_render_completed.emit(self.__output_file, thumbnail_image, metadata)

    def _execute_render_command(self, command: list) -> bool:
        """
        Execute a render command using subprocess.

        :param command: Command to execute.
        :type command: list
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        out, error = process.communicate()

        if error and not out:
            self.signals.on_render_error.emit(str(error.decode()))
            return False
        return True

    def _generate_thumbnail(self, thumbnail_frame_time: float, thumbnail_image: str, input_file: str) -> bool:
        """
        Generate a thumbnail from a video or image sequence.

        :param thumbnail_frame_time: Time to extract the thumbnail frame.
        :type thumbnail_frame_time: float
        :param thumbnail_image: Path to save the thumbnail.
        :type thumbnail_image: str
        :param input_file: Path to the input file.
        :type input_file: str
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        command = _commands.extract_image_from_video(input_file,
                                                     thumbnail_image,
                                                     self.__thumb_resolutionX,
                                                     self.__thumb_resolutionY,
                                                     thumbnail_frame_time)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        _, error = process.communicate()

        if error:
            self.signals.on_render_error.emit(str(error.decode()))
            return False

        time.sleep(0.5)
        return True
