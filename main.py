"""_summary_
"""

import sys
from PySide2 import QtWidgets

from ui import assembleUI
from data import tool_data


class Ulaavi(QtWidgets.QWidget, assembleUI.MainUI):
    """
    Show Thumbnail
    """

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.data = tool_data.Data.get_instance()
        self._widget_connections()

    def _widget_connections(self):
        self.categories.group.on_group_new.connect(self.data.add_group)
        self.categories.group.on_group_remove.connect(self.data.remove_group)
        self.categories.group.on_group_change.connect(self.categories.on_change_group)
        self.categories.tree.on_change.connect(self.on_chnage_current_item)
        self.categories.tree.on_remove.connect(self._on_delete)

        self.categories.tree.on_rename.connect(
            lambda group, old_category, category: self.data.rename_category(group, old_category, category))
        self.categories.tree.on_create.connect(lambda group, category: self.data.add_category(group, category))
        self.categories.group.add_groups(self.data.groups())

    def on_chnage_current_item(self, group, category):
        print('CH: ', group, category)

    def _on_delete(self, group, category):
        self.data.remove_category(group, category)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    cm = Ulaavi()
    cm.show()

    app.exec_()
