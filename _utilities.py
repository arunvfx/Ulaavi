"""
This module provides utility functions for managing files, directories, and proxy files in a media production pipeline.
It includes functionality for deleting files, generating proxy file paths, handling image sequences, and interacting
with the operating system's file explorer. The module is designed to work across multiple platforms
(Windows, macOS, Linux) and integrates with third-party libraries like clique for file sequence management.
"""

# -------------------------------- built-in Modules ----------------------------------
import os
import re
import shutil
import subprocess
import sys

# ------------------------------- ThirdParty Modules ---------------------------------
import clique

try:
    from PySide2 import QtWidgets
except ModuleNotFoundError:
    from PySide6 import QtWidgets

# -------------------------------- Custom Modules ------------------------------------
from data import config


def make_directory(file_path: str) -> None:
    """
    Creates the directory for the given file or directory path if it does not already exist.

    This function ensures that the directory for the provided file or directory path exists.
    If the path points to a file, it extracts the parent directory. If the directory does not exist,
    it creates the directory recursively.

    :param file_path: The path to the file or directory.
    :type file_path: str

    :return: None
    :rtype: None

    :note:
        - If the path points to a file, the parent directory is created.
        - If the path points to a directory, the directory itself is created.
        - If the directory already exists, no action is taken.
    """
    if os.path.isfile(file_path) or len(os.path.splitext(file_path)) == 2:
        file_path = os.path.dirname(file_path)
    if os.path.isdir(file_path) is False:
        os.makedirs(file_path)


def delete_files(files) -> None:
    """
    Deletes the specified files or directories.

    This function can handle both single files/directories and lists of files/directories.
    If a file or directory cannot be deleted, the error is silently ignored.

    :param files: A single file/directory path (str) or a list of file/directory paths.
    :type files: str or list[str] or set[str]
    """

    if isinstance(files, str):
        files = [files]

    for file in files:
        try:
            _remove(file)
        except (OSError, shutil.Error) as error:
            print(error)
            pass


def _remove(file_path):
    """
    Removes a file or directory.

    :param file_path: The path to the file or directory to remove.
    :type file_path: str
    """
    if os.path.isfile(file_path):
        os.remove(file_path)
    elif os.path.isdir(file_path):
        shutil.rmtree(file_path)


def get_proxy_thumbnail(proxy_file: str):
    """
   Generates the thumbnail file path for a given proxy file.

   This function takes a proxy file path and returns the corresponding thumbnail file path.
   If the proxy file is a `.mov` file, the thumbnail is assumed to be a `.png` file with the same base name.
   Otherwise, the original proxy file path is returned.

   :param proxy_file: The path to the proxy file.
   :type proxy_file: str

   :return: The path to the thumbnail file if the proxy file is a `.mov` file; otherwise, the original proxy file path.
            Returns `None` if `proxy_file` is empty or `None`.
   :rtype: str or None

   :note:
       - The function assumes that `.mov` files have corresponding `.png` thumbnails.
       - If `proxy_file` is `None` or an empty string, the function returns `None`.
   """
    if not proxy_file: return
    return proxy_file.replace('.mov', '.png') if proxy_file.endswith('.mov') \
        else proxy_file


def get_dropped_files_with_proxy_path(file_path: str,
                                      proxy_root_path: str,
                                      group: str,
                                      category: str):
    """
   Generates tuples containing source file paths, their corresponding proxy file paths, and a flag indicating whether the source is an image sequence.

   This function processes a given file or directory and yields tuples containing:
   - The source file path.
   - The corresponding proxy file path (generated using `get_proxy_files_from_source_file`).
   - A boolean flag indicating whether the source is part of an image sequence.

   :param file_path: The path to the file or directory to process.
   :type file_path: str
   :param proxy_root_path: The root directory where proxy files are stored.
   :type proxy_root_path: str
   :param group: The group name used to organize proxy files (e.g., project or department).
   :type group: str
   :param category: The category of the source file, used to create subdirectories for proxy files.
                   The category string is split by '|' to create nested directories.
   :type category: str

   :yield: A tuple containing:
       - The source file path (str).
       - The proxy file path (str).
       - A boolean flag indicating whether the source is an image sequence (bool).
   :ytype: tuple

   :note:
       - If `file_path` is a file, it is processed directly.
       - If `file_path` is a directory, it is scanned for image sequences using `get_image_sequence`.
       - The proxy file path is generated using `get_proxy_files_from_source_file`.
       - The boolean flag is `True` for image sequences and `False` for individual files.
   """
    if os.path.isfile(file_path):
        proxy_file = get_proxy_files_from_source_file(
            file_path, proxy_root_path, group, category, is_image_sequence=False)
        if proxy_file:
            yield file_path, proxy_file, False

    elif os.path.isdir(file_path):
        for source_data in get_image_sequence(file_path):

            if isinstance(source_data, tuple):
                proxy_file = get_proxy_files_from_source_file(
                    source_data[0], proxy_root_path, group, category, is_image_sequence=True)
                if proxy_file:
                    yield f'{source_data[0]} {source_data[1]}', proxy_file, True

            if isinstance(source_data, str):
                proxy_file = get_proxy_files_from_source_file(
                    source_data, proxy_root_path, group, category, is_image_sequence=False)
                if proxy_file:
                    yield source_data, proxy_file, False


def get_image_sequence(file_directory: str):
    """
    Generates file paths for image sequences and individual media files in the specified directory.

    This function uses the `clique.assemble` method to identify and group files into sequences (e.g., image sequences)
    based on their naming patterns. It also handles individual files that do not belong to any sequence.

    :param file_directory: The directory path where the files are located.
    :type file_directory: str

    :yield:
        - For image sequences: A tuple containing the base file path (without frame numbers)
          and the frame range as a string (e.g., `('path/to/file', '1-10')`).
        - For individual files: The full file path as a string (e.g., `'path/to/file.ext'`).
    :ytype: tuple or str

    :note:
        - Supported image and video formats are determined by `config.SUPPORTED_IMAGE_FORMATS`
          and `config.SUPPORTED_VIDEO_FORMATS`.
        - The function is case-insensitive on Windows and macOS platforms due to filesystem limitations.
    """
    collections, remainders = clique.assemble(os.listdir(file_directory),
                                              case_sensitive=sys.platform not in ('win32', 'darwin'))

    for collection in collections:
        filename_split = str(collection).split(' [')
        file_name = filename_split[0]

        if file_name.endswith(config.SUPPORTED_IMAGE_FORMATS):
            yield f'{file_directory}/{file_name}', filename_split[-1][:-1]

    for remainder in remainders:
        file_path = f'{file_directory}/{remainder}'

        if file_path.endswith(config.SUPPORTED_IMAGE_FORMATS) or file_path.endswith(config.SUPPORTED_VIDEO_FORMATS):
            yield file_path


def get_proxy_files_from_source_file(source_file: str,
                                     proxy_root_path: str,
                                     group: str,
                                     category: str,
                                     is_image_sequence: bool = False) -> str:
    """
    Generates the proxy file path based on the source file and provided parameters.

    This function constructs a proxy file path using the `source_file`, `proxy_root_path`, `group`, and `category`.
    The proxy file format is determined by the source file's type (image sequence, video, or image).

    :param source_file: The path to the source file for which the proxy file is being generated.
    :type source_file: str
    :param proxy_root_path: The root directory where proxy files are stored.
    :type proxy_root_path: str
    :param group: The group name used to organize proxy files (e.g., project or department).
    :type group: str
    :param category: The category of the source file, used to create subdirectories for proxy files.
                     The category string is split by '|' to create nested directories.
    :type category: str
    :param is_image_sequence: Whether the source file is part of an image sequence. Defaults to False.
    :type is_image_sequence: bool

    :return: The generated proxy file path. If the proxy file does not exist, the path is returned with normalized slashes.
    :rtype: str

    :note:
        - Supported image formats are determined by `config.SUPPORTED_IMAGE_FORMATS`.
        - Supported video formats are determined by `config.SUPPORTED_VIDEO_FORMATS`.
        - If the source file is part of an image sequence or is a video, the proxy file will have a `.mov` extension.
        - If the source file is an image, the proxy file will have a `.png` extension.
    """
    proxy_file_dirs = '/'.join(category.split('|')[1:])

    proxy_file = f'{proxy_root_path}/{group}/{proxy_file_dirs}/{os.path.basename(os.path.splitext(source_file)[0])}'

    if is_image_sequence or source_file.endswith(config.SUPPORTED_VIDEO_FORMATS):
        proxy_file += '.mov'

    elif source_file.endswith(config.SUPPORTED_IMAGE_FORMATS):
        proxy_file += '.png'

    if not os.path.isfile(proxy_file):
        return proxy_file.replace('\\', '/')


def open_in_explorer(file_path: str) -> None:
    """
   Opens the directory containing the specified file in the system's file explorer.

   This function opens the parent directory of the given file in the default file explorer
   for the operating system. It supports Windows, macOS, and Linux platforms.

   :param file_path: The path to the file whose parent directory should be opened.
   :type file_path: str

   :return: None

   :note:
       - On **Windows**, the file explorer opens with the file pre-selected.
       - On **macOS**, the parent directory is opened in Finder.
       - On **Linux**, the parent directory is opened using the default file manager (via `xdg-open`).
       - The `file_path` is normalized using `get_source_file_path` before processing.
   """
    file_path = get_source_file_path(file_path)

    if sys.platform == "win32":
        subprocess.Popen(r'explorer /select, "{}"'.format(file_path.strip().replace("/", "\\")))
    if sys.platform == "darwin":
        os.system("open '{}'".format(os.path.dirname(file_path)))
    if sys.platform == "linux2":
        os.system("xdg-open '{}'".format(os.path.dirname(file_path)))


def get_source_file_path(file_path: str) -> str:
    """
   Retrieves the source file directory if the given file is part of an image sequence; otherwise, returns the file path itself.

   This function checks if the provided file path matches the pattern of an image sequence (e.g., `file_0001-0100`).
   If it does, it returns the directory of the source file. Otherwise, it returns the original file path.

   :param file_path: The path to the file or image sequence.
   :type file_path: str

   :return: The directory of the source file if it is part of an image sequence; otherwise, the original file path.
   :rtype: str

   :note:
       - The function uses a regular expression to detect image sequences based on the pattern `\d{1,9}-\d{1,9}$`.
       - If the file is part of an image sequence, the function extracts the base file path (without the sequence range).
   """
    if re.match(r" \d{1,9}-\d{1,9}$", file_path):
        return os.path.dirname(file_path.rsplit(' ')[0])

    return file_path
