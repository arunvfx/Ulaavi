# -------------------------------- built-in Modules ----------------------------------

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets, QtCore
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore

# -------------------------------- Custom Modules ------------------------------------
from ui import categoriesUI, settingsUI, actionsUI, thumbnailUI


class MainUI:
    def setupUi(self, mainWidget):
        if not mainWidget.objectName():
            mainWidget.setObjectName("Ulaavi")


        self.categories = categoriesUI.Categories()
        self.actions_ui = actionsUI.ActionsUI()
        self.thumbnail = thumbnailUI.ThumbnailUI()
        self.settings = settingsUI.SettingsUI()

        self.__hLayoutMain = QtWidgets.QHBoxLayout(mainWidget)
        self.__hLayoutMain.setContentsMargins(0, 0, 0, 0)

        self.__frame_main = QtWidgets.QFrame()
        self.__vLayoutMain = QtWidgets.QVBoxLayout(self.__frame_main)

        self.__splitter = QtWidgets.QSplitter()
        self.__splitter.setObjectName("splitter")
        self.__splitter.setOrientation(QtCore.Qt.Horizontal)

        self.__leftFrame = QtWidgets.QFrame(self.__splitter)
        self.__rightFrame = QtWidgets.QFrame(self.__splitter)

        self.__hLayout = QtWidgets.QHBoxLayout(self.__leftFrame)
        self.__vLayout = QtWidgets.QVBoxLayout(self.__rightFrame)

        self.__vLayout.addWidget(self.actions_ui)
        self.__vLayout.addWidget(self.thumbnail)
        self.__hLayout.addWidget(self.categories)

        self.__leftFrame.setFocusPolicy(QtCore.Qt.NoFocus)
        self.__leftFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.__leftFrame.setFrameShadow(QtWidgets.QFrame.Plain)

        self.__rightFrame.setFocusPolicy(QtCore.Qt.NoFocus)
        self.__rightFrame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.__rightFrame.setFrameShadow(QtWidgets.QFrame.Plain)

        self.__vLayoutMain.addWidget(self.__splitter)

        self.__vLayoutMain.setContentsMargins(0, 0, 0, 0)
        self.__hLayout.setContentsMargins(0, 0, 0, 0)
        self.__vLayout.setContentsMargins(0, 0, 0, 0)
        self.__splitter.setContentsMargins(0, 0, 0, 0)

        self.__hLayoutMain.addWidget(self.__frame_main)
        self.__hLayoutMain.addWidget(self.settings)

        self._set_widget_connections()

    def _set_widget_connections(self):
        self.actions_ui.on_settings.connect(self._toggle_settings_widget)
        self.settings.on_close.connect(self.__frame_main.show)

    def _toggle_settings_widget(self):
        self.settings.toggle_widget_visibility()
        self.__frame_main.hide()
