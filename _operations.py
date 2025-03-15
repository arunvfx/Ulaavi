from data import tool_data
import _parse_data
from conversion import convert_mov
from PySide2 import QtCore


class Operations:

    def __init__(self, ui):
        self.ui = ui
        self.data = tool_data.Data()
        self.render_signals = RenderSignals()

    def execute_on_startup(self):
        self.ui_add_group()
        self.ui_add_category()
        self.update_thumbnail_scale()

    def update_thumbnail_scale(self):
        # set thumbnail width and height
        scale = self.data.preferences.thumbnail if self.data.preferences.thumbnail == 1 \
            else self.data.preferences.thumbnail * 0.51

        self.ui.thumbnail.cell_width = int(250 * scale)
        self.ui.thumbnail.cell_height = int(200 * scale)
        self.ui.thumbnail.calculate_column()

    def ui_add_group(self):
        self.ui.categories.group.add_groups(self.data.groups())

    def ui_add_category(self):
        group = self.ui.categories.group.current_group
        if not group:
            return

        self.ui.categories.tree.add_categories(list(self.data.categories(group)))

    def on_delete(self, group: str, category: str):
        self.data.remove_category(group, category)

    def on_add_group(self, group: str):
        self.data.add_group(group)

    def on_remove_group(self, group: str):
        self.data.remove_group(group)

    def on_change_group(self, group: str):
        self.ui.categories.on_change_group(group_name=group)
        self.ui_add_category()

    def on_change_category(self, group: str, category: str):
        self.ui.thumbnail.current_category = category if category and category != 'root' else None
        self.ui.thumbnail.reset_table()

    def on_add_category(self, group: str, category: str):
        self.data.add_category(group, category)

    def on_rename_category(self, group: str, old_category: str, new_category: str):
        self.data.rename_category(group, old_category, new_category)

    def on_open_settings(self):
        self.ui.settings.preferences_grp.update_pref_ui(self.data.preferences)

    def on_reset_preferences(self):
        self.ui.settings.preferences_grp.update_pref_ui(self.data.preferences.default_values())

    def on_apply_preferences(self, data: dict):
        self.data.preferences.update(data)
        self.data.refresh()
        self.execute_on_startup()

    def on_file_drop(self, file_url: str):
        """
        on file drop event in table widget, parse the data.

        :param file_url: file url
        :type file_url: str
        :return: parsed data
        :rtype: str
        """
        category = self.ui.categories.tree.item_user_role
        group = self.ui.categories.group.current_group

        data = _parse_data.get_dropped_files_with_proxy_path(
            file_path=file_url,
            proxy_root_path=self.data.preferences.proxy,
            group=group,
            category=category)

        self.ui.thumbnail.dropped_data(data)

    def on_drop_convert_to_mov(self, source_file: str, proxy_file: str, cell_position: tuple, is_image_seq: bool):

        thread_run = convert_mov.ConvertMov(
            source_file, proxy_file, is_image_seq, self.data.preferences.res_width, self.data.preferences.res_height)

        thread_run.signals.on_render_completed.connect(self.on_render_completed)
        thread_run.signals.on_render_error.connect(self.on_render_error)

        self.ui.thumbnail.threadpool.setMaxThreadCount(int(self.data.preferences.thread_count))
        self.ui.thumbnail.threadpool.start(thread_run)

    def on_render_completed(self, data):

        self.render_signals.on_render_completed.emit(data)
        # print('COMPLETED: ', data)

    def on_render_error(self, data):
        print('ERROR: ', data)


class RenderSignals(QtCore.QObject):

    on_render_completed = QtCore.Signal(str)