import concurrent.futures
import os.path
import subprocess
import json
from data import config
from . import _commands
from PySide2 import QtCore


def _get_file_data(source_file):
    cmds = _commands.extract_video_thumbnail_frame(source_file)
    process = subprocess.Popen(cmds, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out, err = process.communicate()

    thumbnail_frame_time = 1
    fps = 24

    if out:
        out = json.loads(out)
        if not out:
            return thumbnail_frame_time, fps

        fps = _get_fps(out['streams'][0]['r_frame_rate'])
        thumbnail_frame_time = round(float(out['streams'][0]['duration']) // 2)

    return thumbnail_frame_time, fps


def _get_fps(frame_rate):
    raw_fps = tuple(map(int, frame_rate.split('/')))
    return raw_fps[0] / raw_fps[1]


def _make_directory(file_path: str):
    path_ = os.path.dirname(file_path)
    if os.path.isdir(path_) is False:
        os.makedirs(path_)


class Signals(QtCore.QObject):
    on_render_completed = QtCore.Signal(str)
    on_render_error = QtCore.Signal(str)


class ConvertMov(QtCore.QRunnable):

    def __init__(self, source_file: str, output_file: str, is_image_seq: bool, resolutionX: int, resolutionY: int):
        super().__init__()
        self.signals = Signals()

        self.__source_file = source_file
        self.__output_file = output_file
        self.__is_image_seq = is_image_seq
        self.__resolutionX = resolutionX
        self.__resolutionY = resolutionY

    def run(self):
        _make_directory(self.__output_file)

        if self.__is_image_seq or self.__source_file.endswith(config.supported_video_formats):
            thumbnail_frame_time, fps = _get_file_data(self.__source_file)

            if not self.__is_image_seq:
                command = _commands.convert_video(
                    self.__source_file, self.__output_file, self.__resolutionX, self.__resolutionY, fps)

                process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                out, error = process.communicate()
                if out:
                    # print(out.decode())
                    self.signals.on_render_completed.emit(str(out.decode()))

                if error:
                    # print(error.decode())
                    self.signals.on_render_error.emit(str(error.decode()))
