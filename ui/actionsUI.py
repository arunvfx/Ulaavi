# -------------------------------- built-in Modules ----------------------------------
from pathlib import Path

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore, QtGui


# -------------------------------- Custom Modules ------------------------------------


class ActionsUI(QtWidgets.QWidget):
    on_settings = QtCore.Signal()

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
        self._set_widget_connections()

    def _set_widget_properties(self):
        self.btn_settings.setFixedHeight(26)
        self.btn_settings.setFlat(True)
        self.btn_settings.setFixedSize(QtCore.QSize(26, 26))
        self.btn_settings.setIcon(QtGui.QIcon(f'{Path(__file__).parent.parent}/icons/setting.png'))

    def _set_widget_connections(self):
        self.btn_settings.clicked.connect(lambda: self.on_settings.emit())



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
        self.btn_refresh.setIcon(QtGui.QIcon(f'{Path(__file__).parent.parent}/icons/refresh.png'))
        self.btn_snap_script.setIcon(QtGui.QIcon(f'{Path(__file__).parent.parent}/icons/capture.png'))
        self.setFocusPolicy(QtCore.Qt.NoFocus)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setFrameShadow(QtWidgets.QFrame.Plain)
        self.__hLayout.setContentsMargins(0, 0, 0, 0)


class Filters(QtWidgets.QFrame):
    on_tags_filter_changed = QtCore.Signal(str, str)
    on_change_search_text = QtCore.Signal(str, str)

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
        self._Set_widget_connections()

    @property
    def current_tag(self):
        tag = self.cmb_tags.currentText()
        return tag if tag.strip() != '-' else ''

    @property
    def search_text(self):
        return self.lineEdit_search.text()

    def _set_widget_properties(self):
        self.cmb_tags.setFixedHeight(26)
        self.lineEdit_search.setFixedHeight(26)
        self.lineEdit_search.setFrame(QtWidgets.QFrame.NoFrame)

    def _Set_widget_connections(self):
        self.cmb_tags.currentIndexChanged.connect(self._on_change_current_index)
        self.lineEdit_search.textChanged.connect(self._on_change_current_index)

    def _on_change_current_index(self):
        self.on_tags_filter_changed.emit(self.current_tag, self.lineEdit_search.text().strip())

    def _on_change_search_text(self):
        current_text = self.lineEdit_search.text().strip()
        if current_text:
            self.on_change_search_text.emit(self.current_tag, self.lineEdit_search.text().strip())

    def add_tags(self, tags: list) -> None:
        self.cmb_tags.clear()
        tags.insert(0, '-'.center(10, ' '))
        self.cmb_tags.addItems(tags)
