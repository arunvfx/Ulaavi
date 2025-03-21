"""
Settings User Interface Module
=============================

This module provides the settings user interface for the application, allowing users to configure
preferences and other settings. It includes a preferences group and handles visibility toggling.

Key Features:
    - **Preferences Group**: A widget for managing application preferences.
    - **Visibility Toggle**: Allows showing or hiding the settings widget.
    - **Close Signal**: Emits a signal when the settings widget is closed.

Usage:
    - Use the `toggle_widget_visibility` method to show or hide the settings widget.
    - Connect to the `on_close` signal to handle actions when the settings widget is closed.
"""

# -------------------------------- built-in Modules ----------------------------------

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets, QtCore
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore

# -------------------------------- Custom Modules ------------------------------------
from . import _preferences_grp_ui


class SettingsUI(QtWidgets.QWidget):
    """
    Settings user interface class for managing application preferences.
    This widget provides a preferences group and handles visibility toggling.

    Signals:
    --------
    on_close : Signal()
        Emitted when the settings widget is closed.
    """

    on_close = QtCore.Signal()

    def __init__(self):
        super().__init__()

        self.__vLayout = QtWidgets.QVBoxLayout(self)
        self.preferences_grp = _preferences_grp_ui.Preferences()
        self.vSpacer = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.__vLayout.addWidget(self.preferences_grp)
        self.__vLayout.addItem(self.vSpacer)

        self.hide()
        self._set_widget_connection()

    def _set_widget_connection(self) -> None:
        """
        Set up signal connections for the settings widget.
        This method connects the close button to the `close` method.
        """
        self.preferences_grp.btn_close.clicked.connect(self.close)

    def close(self) -> None:
        """
        Close the settings widget.
        This method toggles the widget's visibility and emits the `on_close` signal.
        """
        self.toggle_widget_visibility()
        self.on_close.emit()

    def toggle_widget_visibility(self) -> None:
        """
        Toggle the visibility of the settings widget.
        This method shows the widget if it is hidden, or hides it if it is visible.
        """
        self.hide() if self.isVisible() else self.show()
