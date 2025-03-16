"""
_summary_

:return: _description_
:rtype: _type_
"""
import sys

sys.path.append('C:/Users/arunv/Documents/MyWork/ulaavi/v002/Ulaavi/.venv/Lib/site-packages')
import clique
import os
import sys
import subprocess
from data import config
import re


def get_dropped_files_with_proxy_path(file_path: str,
                                      proxy_root_path: str,
                                      group: str,
                                      category: str):
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
    collections, remainders = clique.assemble(os.listdir(file_directory),
                                              case_sensitive=sys.platform not in ('win32', 'darwin'))

    for collection in collections:
        filename_split = str(collection).split(' [')
        file_name = filename_split[0]

        if file_name.endswith(config.supported_image_formats):
            yield f'{file_directory}/{file_name}', filename_split[-1][:-1]

    for remainder in remainders:
        file_path = f'{file_directory}/{remainder}'

        if file_path.endswith(config.supported_image_formats) or file_path.endswith(config.supported_video_formats):
            yield file_path


def get_proxy_files_from_source_file(source_file: str,
                                     proxy_root_path: str,
                                     group: str,
                                     category: str,
                                     is_image_sequence: bool = False) -> str:
    preview_file_dirs = '/'.join(category.split('|')[1:])

    preview_file = ''

    if is_image_sequence or source_file.endswith(config.supported_video_formats):
        preview_file = (f'{proxy_root_path}/{group}/{preview_file_dirs}/'
                        f'{os.path.basename(os.path.splitext(source_file)[0])}.mov')

    elif source_file.endswith(config.supported_image_formats):
        preview_file = (f'{proxy_root_path}/{group}/{preview_file_dirs}/'
                        f'{os.path.basename(os.path.splitext(source_file)[0])}.png')

    if not os.path.isfile(preview_file):
        return preview_file.replace('\\', '/')


def open_in_explorer(file_path: str) -> None:
    file_path = get_source_file_path(file_path)

    if sys.platform == "win32":
        subprocess.Popen(r'explorer /select, "{}"'.format(file_path.strip().replace("/", "\\")))
    if sys.platform == "darwin":
        os.system("open '{}'".format(os.path.dirname(file_path)))
    if sys.platform == "linux2":
        os.system("xdg-open '{}'".format(os.path.dirname(file_path)))


def get_source_file_path(file_path: str):
    if re.match(r" \d{1,9}-\d{1,9}$", file_path):
        return os.path.dirname(file_path.rsplit(' ')[0])

    return file_path
