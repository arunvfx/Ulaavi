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
        self.__ops = _operations.Operations(self)
        self._widget_connections()
        self.__ops.execute_on_startup()

    def _widget_connections(self):
        self.categories.group.on_group_new.connect(self.__ops.on_add_group)
        self.categories.group.on_group_remove.connect(self.__ops.on_remove_group)
        self.categories.group.on_group_change.connect(self.__ops.on_change_group)
        self.categories.tree.on_change.connect(self.__ops.on_change_category)
        self.categories.tree.on_remove.connect(self.__ops.on_delete)
        self.categories.tree.on_rename.connect(self.__ops.on_rename_category)
        self.categories.tree.on_create.connect(self.__ops.on_add_category)
        self.settings.preferences_grp.on_reset.connect(self.__ops.on_reset_preferences)
        self.actions_ui.on_settings.connect(self.__ops.on_open_settings)
        self.settings.preferences_grp.on_apply.connect(self.__ops.on_apply_preferences)

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
