import sys
from PySide2 import QtWidgets

from ui._categoriesGroup import CategoriesGroup
from ui._categoriesHeaders import Headers
from ui._categoriesTree import CategoriesTree


class Categories(QtWidgets.QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.group = CategoriesGroup()
        self.header = Headers()
        self.tree = CategoriesTree()
        self.__main_layout = QtWidgets.QVBoxLayout(self)
        self.__main_layout.addWidget(self.group)
        self.__main_layout.addWidget(self.header)
        self.__main_layout.addWidget(self.tree)

        self._set_widget_connections()

    def _set_widget_connections(self) -> None:

        self.header.btn_categories_item_add.clicked.connect(
            self.tree.add_item)
