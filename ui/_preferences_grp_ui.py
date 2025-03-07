# -------------------------------- built-in Modules ----------------------------------
from pathlib import Path

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore, QtGui

# -------------------------------- Custom Modules ------------------------------------
from . import _preferences_grp


class Preferences(_preferences_grp.PreferencesGroup, QtWidgets.QWidget):
    on_reset = QtCore.Signal()
    on_apply = QtCore.Signal(dict)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self._set_widget_connections()
        self._set_widget_properties()

    def _set_widget_properties(self):
        self.btn_browse_json.setIcon(QtGui.QIcon(f'{Path(__file__).parent.parent}/icons/explore.png'))
        self.btn_browse_proxy.setIcon(QtGui.QIcon(f'{Path(__file__).parent.parent}/icons/explore.png'))
        self.btn_browse_proxy.setFlat(True)
        self.btn_browse_json.setFlat(True)

        self.lineEdit_res_width.setValidator(QtGui.QIntValidator(100, 600))
        self.lineEdit_res_height.setValidator(QtGui.QIntValidator(100, 600))
        self.lineEdit_thread_count.setValidator(QtGui.QIntValidator(1, 8))

    def _set_widget_connections(self):
        self.btn_reset.clicked.connect(self._reset_pref)
        self.btn_apply.clicked.connect(self._apply_pref)
        self.btn_browse_proxy.clicked.connect(self._set_proxy_directory)
        self.btn_browse_json.clicked.connect(self._set_json_file_path)

    def _reset_pref(self) -> None:
        self.on_reset.emit()

    def _apply_pref(self) -> None:
        data = {'proxy': self.lineEdit_proxy.text().strip(),
                'data': self.lineEdit_json.text().strip(),
                'thread_count': str(self.lineEdit_thread_count.text().strip()),
                'res_width': str(self.lineEdit_res_width.text().strip()),
                'res_height': str(self.lineEdit_res_height.text().strip()),
                'thumbnail': str(self.slider_thumbnail_scale.value())}

        self.on_apply.emit(data)

    def update_pref_ui(self, data: dict) -> None:
        self.lineEdit_proxy.setText(data.get('proxy') if data.get('proxy') else '')
        self.lineEdit_json.setText(data.get('data') if data.get('data') else '')
        self.lineEdit_thread_count.setText(data.get('thread_count') if data.get('thread_count') else '')
        self.lineEdit_res_width.setText(data.get('res_width') if data.get('res_width') else '')
        self.lineEdit_res_height.setText(data.get('res_height') if data.get('res_height') else '')
        self.slider_thumbnail_scale.setValue(int(data.get('thumbnail')) if data.get('thumbnail') else 1)

    def _set_proxy_directory(self):
        directory = self._browse_proxy_directory()
        if directory:
            self.lineEdit_proxy.setText(directory)

    def _set_json_file_path(self):
        directory = self._browse_proxy_directory()
        if directory:
            self.lineEdit_json.setText(f'{directory}/data.json')

    def _browse_proxy_directory(self):
        file_browser = QtWidgets.QFileDialog(self)

        return file_browser.getExistingDirectory(
            self, "Select Directory", "",
            options=QtWidgets.QFileDialog.DontUseNativeDialog)
