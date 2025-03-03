import sys
from PySide2 import QtWidgets, QtCore

from ui import categoriesUI


class Ulaavi(QtWidgets.QWidget):
    """
    Show Thumbnail
    """

    def __init__(self):
        super().__init__()

        self.hLayout = QtWidgets.QHBoxLayout(self)
        self.hLayout.setContentsMargins(0, 0, 0, 0)

        self.categories = categoriesUI.Categories(self)
        self.hLayout.addWidget(self.categories)

        self.categories.group.new_group.connect(self.on_create_group)
        self.categories.group.group_change_event.connect(self.on_change_group)
        self.categories.group.remove_group.connect(self.on_remove_group)

    def on_create_group(self, group_name: str):
        """
        on create group

        :param group_name: group name
        :type group_name: str
        :return: None
        :rtype: None
        """
        print('CREATE GROUP NAME: ', group_name)

    def on_change_group(self, group_name: str):
        """
        on change current group name

        :param group_name: group name
        :type group_name: str
        :return: None
        :rtype: None
        """
        print('CURRENT GROUP NAME: ', group_name)

    def on_remove_group(self, group_name: str):
        """
        on remove group

        :param group_name: group name
        :type group_name: str
        :return: None
        :rtype: NOne
        """
        print('REMOVE GROUP: ', group_name)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    cm = Ulaavi()
    cm.show()

    app.exec_()
