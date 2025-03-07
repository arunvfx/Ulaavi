# -------------------------------- built-in Modules ----------------------------------

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets, QtCore
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore

# -------------------------------- Custom Modules ------------------------------------
from . import _preferences_grp_ui


class SettingsUI(QtWidgets.QWidget):

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

    def _set_widget_connection(self):
        self.preferences_grp.btn_close.clicked.connect(self.close)

    def close(self):
        self.toggle_widget_visibility()
        self.on_close.emit()

    def toggle_widget_visibility(self):
        """
        toggle settings widget visibility

        :return: None
        :rtype: None
        """
        self.hide() if self.isVisible() else self.show()
