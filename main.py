"""_summary_
"""

import sys
from PySide2 import QtWidgets, QtCore

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
        # self.categories.group.on_group_change.connect(self.categories.on_change_group)
        self.categories.tree.on_rename.connect(self.on_category_create)
        # self.categories.tree.is_category_exists.connect(
        #     lambda group, category: self.categories.tree.update_category_exists(
        #         self.data.is_category_exists(group, category))
        # )
        self.categories.tree.is_category_exists.connect(self.on_rename)
        self.categories.group.add_groups(self.data.groups())

    def on_category_create(self, group_name, old_name, category_name):
        print(f'GN: {group_name}   OLD: {old_name}   ,Category: {category_name}')

    def on_rename(self, group, category):
        t = self.data.is_category_exists(group, category)
        print(t)
        # self.categories.tree.update_category_exists(



if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    cm = Ulaavi()
    cm.show()

    app.exec_()
