import sys
from PySide2 import QtWidgets, QtCore, QtGui


class CategoriesTree(QtWidgets.QTreeWidget):
    """
    Categories
    """
    def __init__(self, parent=None) -> None:
        super().__init__()

        self._set_widget_properties()

    def _set_widget_properties(self) -> None:
        """
        set QTreeWidget properties
        :return: None
        """
        self.setColumnCount(1)
        # self.tree_category.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

    def add_item(self) -> None:
        """
        add item into QTreeWidget
        :return: None
        """
        print('add item!')
