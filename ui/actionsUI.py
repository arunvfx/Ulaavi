from pathlib import Path
from PySide2 import QtWidgets, QtCore, QtGui


class ActionsUI(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.__hLayout = QtWidgets.QHBoxLayout(self)
        self.actions = Actions(self)
        self.filters = Filters(self)

        self.btn_settings = QtWidgets.QPushButton()

        self.__hLayout.addWidget(self.actions)
        self.__hLayout.addWidget(self.filters)
        self.__hLayout.addWidget(self.btn_settings)

        self._set_widget_properties()

    def _set_widget_properties(self):
        self.btn_settings.setFixedHeight(26)
        self.btn_settings.setFlat(True)
        self.btn_settings.setFixedSize(QtCore.QSize(26, 26))
        self.btn_settings.setIcon(QtGui.QIcon(f'{Path.cwd()}/icons/setting.png'))


class Actions(QtWidgets.QFrame):

    on_snap_script = QtCore.Signal()
    on_refresh = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.btn_snap_script = QtWidgets.QPushButton()
        self.btn_refresh = QtWidgets.QPushButton()

        self.__hLayout = QtWidgets.QHBoxLayout(self)
        self.__hLayout.addWidget(self.btn_snap_script)
        self.__hLayout.addWidget(self.btn_refresh)

        self._set_widget_properties()

    def _set_widget_properties(self):
        self.btn_refresh.setFlat(True)
        self.btn_snap_script.setFlat(True)
        self.btn_refresh.setFixedSize(QtCore.QSize(26, 26))
        self.btn_snap_script.setFixedSize(QtCore.QSize(26, 26))
        self.btn_refresh.setIcon(QtGui.QIcon(f'{Path.cwd()}/icons/refresh.png'))
        self.btn_snap_script.setIcon(QtGui.QIcon(f'{Path.cwd()}/icons/capture.png'))
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setFrameShadow(QtWidgets.QFrame.Plain)
        self.__hLayout.setContentsMargins(0, 0, 0, 0)


class Filters(QtWidgets.QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.lbl_tags = QtWidgets.QLabel('\tTags')
        self.cmb_tags = QtWidgets.QComboBox()

        self.lineEdit_search = QtWidgets.QLineEdit()
        self.lineEdit_search.setPlaceholderText('Search here...')

        self.__hLayout = QtWidgets.QHBoxLayout(self)
        self.__hLayout.addWidget(self.lbl_tags)
        self.__hLayout.addWidget(self.cmb_tags)
        self.__hLayout.addWidget(self.lineEdit_search)

        self._set_widget_properties()

    def _set_widget_properties(self):
        self.cmb_tags.setFixedHeight(26)
        self.lineEdit_search.setFixedHeight(26)
        self.lineEdit_search.setFrame(QtWidgets.QFrame.NoFrame)

    def add_tags(self, tags: list or tuple) -> None:
        self.cmb_tags.addItems(tags)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])

    a = ActionsUI()
    a.show()
    app.exec_()
