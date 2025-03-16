# -------------------------------- built-in Modules ----------------------------------
import sys

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets, QtCore
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore

# -------------------------------- Custom Modules ------------------------------------
from ui import mainUI
import _operations


class Ulaavi(QtWidgets.QWidget, mainUI.MainUI):
    """
    Show Thumbnail
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.resize(1400, 700)

        self.__ops = _operations.Operations()
        self._widget_connections()
        self.execute_on_startup()

    def _widget_connections(self):
        # update status
        self.__ops.op_signals.update_status.connect(self.status.set_status)

        # on create group
        self.categories.group.on_group_new.connect(self.__ops.on_create_group)
        self.categories.group.on_group_new.connect(self.__ops.on_create_group)

        # on remove group
        self.categories.group.on_group_remove.connect(self.__ops.on_remove_group)

        # on change group
        self.categories.group.on_group_change.connect(self.__ops.ui_add_category)

        # on create category
        self.categories.tree.on_create.connect(self.__ops.on_create_category)

        # on delete category
        self.categories.tree.on_remove.connect(self.__ops.on_delete)

        # on rename category
        self.categories.tree.on_rename.connect(self.__ops.on_rename_category)

        self.categories.tree.on_change.connect(self.__ops.on_change_category)

        self.settings.preferences_grp.on_reset.connect(self.__ops.on_reset_preferences)
        self.actions_ui.on_settings.connect(self.__ops.on_open_settings)
        self.settings.preferences_grp.on_apply.connect(self.__ops.on_apply_preferences)
        self.thumbnail.on_drop.connect(self.__ops.on_file_drop)
        self.thumbnail.on_drop_convert_mov.connect(self.__ops.convert_to_mov)
        self.thumbnail.on_context_menu.connect(self.__ops.on_load_tags)
        self.thumbnail.on_open_in_explorer.connect(self.__ops.on_open_in_explorer)
        self.thumbnail.on_recache_proxy.connect(self.__ops.on_recache_proxy)

        self.__ops.op_signals.execute_startup.connect(self.execute_on_startup)
        self.__ops.op_signals.on_files_dropped.connect(self.thumbnail.dropped_data)
        self.__ops.op_signals.on_recache_proxy.connect(self.thumbnail.dropped_data)
        self.__ops.op_signals.on_load_groups.connect(self.categories.group.add_groups)
        self.__ops.op_signals.on_load_categories.connect(self.categories.tree.add_categories)
        self.__ops.op_signals.on_change_category.connect(self.thumbnail.load_thumbnails)
        self.__ops.op_signals.thumbnail_scale.connect(self.thumbnail.update_thumbnail_scale)
        self.__ops.op_signals.on_open_settings.connect(self.settings.preferences_grp.update_pref_ui)
        self.__ops.op_signals.on_reset_preferences.connect(self.settings.preferences_grp.update_pref_ui)
        self.__ops.op_signals.on_render_completed.connect(self.thumbnail.on_render_completed)
        self.__ops.op_signals.on_start_conversion.connect(self.thumbnail.start_thread)
        self.__ops.op_signals.on_load_tags.connect(self.thumbnail.set_tags)

    def execute_on_startup(self):
        self.__ops.ui_add_group()
        self.__ops.ui_add_category(self.categories.group.current_group)
        self.__ops.update_thumbnail_scale()
        self.thumbnail.max_thread_count = int(self.__ops.data.preferences.thread_count)
        self.__ops.update_thumbnail_scale()

    def event(self, event):
        if event.type() == QtCore.QEvent.Type.Show:
            try:
                set_widget_margins(self)
            except:
                pass
        return QtWidgets.QWidget.event(self, event)


def set_widget_margins(widget_object):
    if widget_object:
        target_widgets = set()
        target_widgets.add(widget_object.parentWidget().parentWidget())
        target_widgets.add(widget_object.parentWidget().parentWidget().parentWidget().parentWidget())

        for widget_layout in target_widgets:
            try:
                widget_layout.layout().setContentsMargins(0, 0, 0, 0)
            except Exception as error:
                print(error)


def main():
    main.e = Ulaavi()
    main.e.show()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    cm = Ulaavi()
    cm.show()

    app.exec_()
