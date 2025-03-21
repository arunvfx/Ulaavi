"""
This module provides a `Preferences` widget for managing application settings in a Qt-based application.

The `Preferences` widget allows users to:
- Set and update preferences such as proxy directory, JSON file path, thread count, resolution, and thumbnail scale.
- Browse and select directories for proxy and JSON file paths.
- Reset preferences to their default values.
- Apply changes and emit signals for integration with other parts of the application.

Key Features:
- **Preference Management**: Provides input fields for proxy directory, JSON file path, thread count, resolution,
  and thumbnail scale.
- **Directory Browsing**: Allows users to browse and select directories for proxy and JSON file paths.
- **Signals**: Emits signals when preferences are reset or applied.
- **Validation**: Ensures valid input for thread count and resolution fields.

Dependencies:
- **PySide2/PySide6**: For Qt-based GUI functionality.
- **Custom Modules**: `_preferences_grp` for the base UI layout.

"""

# -------------------------------- built-in Modules ----------------------------------
from pathlib import Path

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets, QtCore, QtGui
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore, QtGui

# -------------------------------- Custom Modules ------------------------------------
from . import _preferences_grp
from data import config


class Preferences(_preferences_grp.PreferencesGroup, QtWidgets.QWidget):
    """
    A widget for managing application preferences.

    This class provides a user interface for setting and updating application preferences,
    such as proxy directory, JSON file path, thread count, resolution, and thumbnail scale.
    It emits signals when preferences are reset or applied.

    Signals:
        on_reset: Emitted when the reset button is clicked.
        on_apply (dict): Emitted when the apply button is clicked, carrying the updated preferences.
    """
    on_reset = QtCore.Signal()
    on_apply = QtCore.Signal(dict)

    def __init__(self):
        """
        Initialize the Preferences widget.

        Sets up the UI, connects signals to slots, and configures widget properties.
        """
        super().__init__()
        self.setupUi(self)

        self._set_widget_connections()
        self._set_widget_properties()

    def _set_widget_properties(self) -> None:
        """
        Configure widget properties, such as icons, validators, and styles.
        """
        icon_root_dir = Path(__file__).parent.parent
        self.btn_browse_json.setIcon(QtGui.QIcon(f'{icon_root_dir}/icons/explore.png'))
        self.btn_browse_proxy.setIcon(QtGui.QIcon(f'{icon_root_dir}/icons/explore.png'))
        self.btn_browse_proxy.setFlat(True)
        self.btn_browse_json.setFlat(True)

        self.lineEdit_res_width.setValidator(QtGui.QIntValidator(100, 600))
        self.lineEdit_res_height.setValidator(QtGui.QIntValidator(100, 600))
        self.lineEdit_thread_count.setValidator(QtGui.QIntValidator(1, 8))

    def _set_widget_connections(self) -> None:
        """
        Connect widget signals to their respective slots.
        """
        self.btn_reset.clicked.connect(self._reset_pref)
        self.btn_apply.clicked.connect(self._apply_pref)
        self.btn_browse_proxy.clicked.connect(self._set_proxy_directory)
        self.btn_browse_json.clicked.connect(self._set_json_file_path)

    def _reset_pref(self) -> None:
        """
        Handle the reset button click event.
        Emits the `on_reset` signal to notify other components.
        """
        self.on_reset.emit()

    def _apply_pref(self) -> None:
        """
        Handle the apply button click event.

        Collects the current preferences from the UI and emits the `on_apply` signal
        with the updated preferences as a dictionary.
        """
        data = {'proxy': self.lineEdit_proxy.text().strip(),
                'data': self.lineEdit_json.text().strip(),
                'thread_count': str(self.lineEdit_thread_count.text().strip()),
                'res_width': str(self.lineEdit_res_width.text().strip()),
                'res_height': str(self.lineEdit_res_height.text().strip()),
                'thumbnail': str(self.slider_thumbnail_scale.value())}

        self.on_apply.emit(data)

    def update_pref_ui(self, data: dict) -> None:
        """
        Update the UI with the provided preferences.

        :param data: A dictionary containing preference values.
        :type data: dict
        """
        self.lineEdit_proxy.setText(data.get('proxy', ''))
        self.lineEdit_json.setText(data.get('data', ''))
        self.lineEdit_thread_count.setText(data.get('thread_count', ''))
        self.lineEdit_res_width.setText(data.get('res_width', ''))
        self.lineEdit_res_height.setText(data.get('res_height', ''))
        self.slider_thumbnail_scale.setValue(int(data.get('thumbnail', 1)))

    def _set_proxy_directory(self) -> None:
        """
        Open a directory dialog to set the proxy directory.

        Updates the proxy directory input field with the selected directory.
        """
        directory = self._browse_proxy_directory()
        if directory:
            self.lineEdit_proxy.setText(directory)

    def _set_json_file_path(self) -> None:
        """
        Open a directory dialog to set the JSON file path.
        Updates the JSON file path input field with the selected directory.
        """
        directory = self._browse_proxy_directory()
        if directory:
            self.lineEdit_json.setText(f'{directory}/{config.DATA_FILE_NAME}')

    def _browse_proxy_directory(self) -> str:
        """
        Open a directory dialog and return the selected directory.

        :return: The selected directory path, or an empty string if canceled.
        :rtype: str
        """
        file_browser = QtWidgets.QFileDialog(self)

        return file_browser.getExistingDirectory(
            self, "Select Directory", "",
            options=QtWidgets.QFileDialog.DontUseNativeDialog)
