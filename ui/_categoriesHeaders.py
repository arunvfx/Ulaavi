import sys

from PySide2 import QtWidgets, QtCore


class Headers(QtWidgets.QFrame):
    """
    Categories headers
    """

    def __init__(self) -> None:
        """
        initialize variables.
        """
        super().__init__()

        self.__layout = QtWidgets.QHBoxLayout(self)
        self.__header_label = QtWidgets.QLabel()

        self.btn_categories_item_add = QtWidgets.QPushButton('+')
        self.btn_categories_item_remove = QtWidgets.QPushButton('-')

        self.__layout.addWidget(self.__header_label)
        self.__layout.addWidget(self.btn_categories_item_add)
        self.__layout.addWidget(self.btn_categories_item_remove)

        self._set_widget_properties()

    def _set_widget_properties(self) -> None:
        self.__header_label.setText('Categories')
        self.__header_label.setAlignment(QtCore.Qt.AlignCenter)

        self.btn_categories_item_remove.setFixedSize(25, 25)
        self.btn_categories_item_add.setFixedSize(25, 25)

        self.__layout.setContentsMargins(0, 0, 0, 0)
        self.__layout.setSpacing(1)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    h = Headers()
    h.show()
    app.exec_()
