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
from data import config


def get_dropped_files_with_proxy_path(file_path: str,
                                      proxy_root_path: str,
                                      group: str,
                                      category: str):
    if os.path.isfile(file_path):
        yield _get_proxy_for_file(file_path, proxy_root_path, group, category)

    elif os.path.isdir(file_path):
        for source_data in get_image_sequence(file_path):
            if isinstance(source_data, tuple):
                proxy_file = get_proxy_files_from_source_file(
                    source_data[0], proxy_root_path, group, category, is_image_sequence=True)
                yield f'{source_data[0]} {source_data[1]}', proxy_file, True

            if isinstance(source_data, str):
                yield _get_proxy_for_file(source_data, proxy_root_path, group, category)


def _get_proxy_for_file(file_path, proxy_root_path, group, category):
    proxy_file = get_proxy_files_from_source_file(
        file_path, proxy_root_path, group, category, is_image_sequence=False)

    return file_path, proxy_file, False


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

    if is_image_sequence or source_file.endswith(config.supported_video_formats):
        preview_file = (f'{proxy_root_path}/{group}/{preview_file_dirs}/'
                        f'{os.path.basename(os.path.splitext(source_file)[0])}.mov')
        return preview_file

    elif source_file.endswith(config.supported_image_formats):
        preview_file = (f'{proxy_root_path}/{group}/{preview_file_dirs}/'
                        f'{os.path.basename(os.path.splitext(source_file)[0])}.png')
        return preview_file
