import os.path
from data import tool_data
import _utilities
from conversion import convert_mov
from functools import partial

try:
    from PySide2.QtCore import QObject, Signal, QRunnable
except ModuleNotFoundError:
    from PySide6.QtCore import QObject, Signal, QRunnable


class OpSignals(QObject):
    execute_startup = Signal()
    thumbnail_scale = Signal(int, int, float)
    update_status = Signal(str)

    on_load_groups = Signal(tuple)
    on_load_categories = Signal(tuple)
    on_change_category = Signal(list)
    on_load_tags = Signal(list)

    on_open_settings = Signal(dict)
    on_reset_preferences = Signal(dict)
    on_start_conversion = Signal(object)
    on_files_dropped = Signal(tuple)
    on_recache_proxy = Signal(tuple)
    on_render_completed = Signal(dict, str, tuple)
    on_change_filters = Signal(list)
    on_delete_proxy = Signal()


class Operations:

    def __init__(self):
        self.data = tool_data.Data()
        self.op_signals = OpSignals()

    def update_thumbnail_scale(self):
        default_width = 320
        font_size = 8

        self.op_signals.thumbnail_scale.emit(
            self._thumbnail_scale_percentage(default_width),
            self._thumbnail_scale_percentage(default_width / 1.89),
            self._scale_font_size(font_size))

    def _thumbnail_scale_percentage(self, initial_value):
        return initial_value if self.data.preferences.thumbnail == 1 \
            else (0.25 * self.data.preferences.thumbnail * initial_value) + initial_value

    def _scale_font_size(self, initial_font_size):
        return initial_font_size if self.data.preferences.thumbnail == 1 \
            else ((0.25 * self.data.preferences.thumbnail * 1) + 1) * initial_font_size

    def ui_add_group(self):
        self.op_signals.on_load_groups.emit(tuple(self.data.groups()))

    def ui_add_category(self, group):
        if not group:
            return

        self.op_signals.on_load_categories.emit(tuple(self.data.categories(group)))

    def on_delete(self, group: str, category: str):
        self.data.remove_category(group, category)
        self.op_signals.update_status.emit(f'Removed Category: {category} from Group: {group}')

    def on_create_group(self, group: str):
        self.data.add_group(group)
        self.op_signals.update_status.emit(f'Created Group: {group}')

    def on_remove_group(self, group: str):
        self.data.remove_group(group)
        self.op_signals.update_status.emit(f'Removed Group: {group}')

    def on_create_category(self, group: str, category: str):
        self.data.add_category(group, category)
        self.op_signals.update_status.emit(f'Created Category: {category} in Group: {group}')

    def on_rename_category(self, group: str, old_category: str, new_category: str):
        self.data.rename_category(group, old_category, new_category)
        self.op_signals.update_status.emit(f'Renamed Category: {old_category} -> {new_category}')

    def on_change_category(self, group: str, category: str, tag: str = None, search_string: str = None):
        if category == 'root':
            return
        self.op_signals.on_change_category.emit(
            self.data.thumbnail_data(group, category, tag=tag, search_string=search_string))

    def on_load_tags(self):
        self.op_signals.on_load_tags.emit(self.data.tags)

    def on_change_filters(self, group: str, category: str, tag: str = '', search_text: str = ''):
        """
        on change tag filter, filter the files by tag and send the files to update on to UI.

        :param group:
        :type group:
        :param category:
        :type category:
        :param tag:
        :type tag:
        :param search_text:
        :type search_text:
        :return:
        :rtype:
        """
        if category == 'root':
            return
        self.op_signals.on_change_filters.emit(
            self.data.thumbnail_data(group, category, tag=tag, search_string=search_text))

    def on_create_tag(self, tag: str):
        self.data.create_tag(tag)
        self.op_signals.update_status.emit(f'Created Tag: {tag}.')
        self.on_load_tags()

    def on_add_tag(self, group: str, category: str, source_files: list, tag: str):
        """
        add selected tag to the  selected files file

        :param group:
        :type group:
        :param category:
        :type category:
        :param source_files:
        :type source_files:
        :param tag:
        :type tag:
        :return:
        :rtype:
        """
        self.data.add_tag(group, category, source_files, tag)

    def on_remove_tag(self, group: str, category: str, source_files: list, tag: str):
        """
        remove selected tag from the  selected files

        :param group:
        :type group:
        :param category:
        :type category:
        :param source_files:
        :type source_files:
        :param tag:
        :type tag:
        :return:
        :rtype:
        """
        self.data.remove_tag(group, category, source_files, tag)

    def on_open_settings(self):
        self.op_signals.on_open_settings.emit(self.data.preferences.preferences())
        self.op_signals.update_status.emit(f'Settings Panel')

    def on_reset_preferences(self):
        self.op_signals.on_reset_preferences.emit(self.data.preferences.default_values())
        self.op_signals.update_status.emit(f'Settings Panel: reset preferences, click "Apply" to save the changes.')

    def on_apply_preferences(self, data: dict):
        self.data.preferences.update(data)
        self.data.refresh()
        self.op_signals.execute_startup.emit()
        self.op_signals.update_status.emit(f'Settings Panel: Saved Preferences.')

    def on_file_drop(self, file_url: str, group: str, category: str):
        """
        on file drop event in table widget, parse the data.

        :param file_url:
        :type file_url:
        :param group:
        :type group:
        :param category:
        :type category:
        :return:
        :rtype:
        """
        data = tuple(_utilities.get_dropped_files_with_proxy_path(
            file_path=file_url,
            proxy_root_path=self.data.preferences.proxy,
            group=group,
            category=category))

        if not data:
            self.op_signals.update_status.emit(f'Proxy already exist for the source file: {file_url}')

        self.op_signals.on_files_dropped.emit(data)

    def on_recache_proxy(self, file_url, cell_position, group, category):
        file_url = _utilities.get_source_file_path(file_url)

        data = tuple(_utilities.get_dropped_files_with_proxy_path(
            file_path=file_url,
            proxy_root_path=self.data.preferences.proxy,
            group=group,
            category=category))

        if not data:
            self.op_signals.update_status.emit(f'Proxy already exist for the source file: {file_url}')

        for i in data:
            self.convert_to_mov(*i, cell_position, group, category)

    def on_delete_proxy(self, group: str, category: str, source_file: list, tag: str = None, search_string: str = None):
        self.data.remove_data(group, category, source_files=source_file)
        self.on_change_category(group, category, tag, search_string)

    def convert_to_mov(self,
                       source_file: str,
                       proxy_file: str,
                       is_image_seq: bool,
                       cell_position: tuple,
                       group: str,
                       category: str):
        if os.path.isfile(proxy_file):
            self.op_signals.update_status.emit(f'Proxy file already exist: {proxy_file}')
            return

        worker = convert_mov.ConvertMov(
            source_file, proxy_file, is_image_seq, self.data.preferences.res_width, self.data.preferences.res_height)
        self.op_signals.on_start_conversion.emit(worker)

        worker.signals.on_render_completed.connect(
            partial(self.on_render_completed,
                    group=group,
                    category=category,
                    source_file=source_file,
                    cell_position=cell_position))

        worker.signals.on_render_error.connect(self.on_render_error)
        self.op_signals.update_status.emit(f'Creating proxy File for {source_file}')

    def on_render_completed(self,
                            proxy_file: str,
                            proxy_thumbnail: str,
                            metadata: dict,
                            group: str,
                            category: str,
                            source_file: str,
                            cell_position: tuple):

        data = self.data.add_thumbnail_data(source_file, proxy_file, metadata, group, category)
        self.op_signals.on_render_completed.emit(data, proxy_thumbnail, cell_position)
        self.op_signals.update_status.emit(f'Created  Proxy File: {proxy_file}')

    def on_render_error(self, data):
        print('ERROR: ', data)

    def on_open_in_explorer(self, file_path: str) -> None:
        _utilities.open_in_explorer(file_path)
