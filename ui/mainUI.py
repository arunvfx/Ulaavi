# -------------------------------- built-in Modules ----------------------------------

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets, QtCore
except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore

# -------------------------------- Custom Modules ------------------------------------
from ui import categoriesUI, settingsUI, actionsUI, thumbnailUI, stausbarUI


class MainUI:
    def setupUi(self, mainWidget):
        if not mainWidget.objectName():
            mainWidget.setObjectName("Ulaavi")

        self.categories = categoriesUI.Categories()
        self.actions_ui = actionsUI.ActionsUI()
        self.thumbnail = thumbnailUI.ThumbnailUI()
        self.settings = settingsUI.SettingsUI()
        self.status = stausbarUI.StatusBar()

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
        self.__vLayoutMain.addWidget(self.status)

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

        self.categories.tree.on_create.connect(self.update_group_attributes)
        self.categories.tree.on_change.connect(self.update_group_attributes)
        self.categories.tree.on_rename.connect(self.update_on_rename_category)

        self.categories.group.on_group_change.connect(self.on_change_group)
        self.categories.group.on_group_new.connect(self.on_change_group)
        self.categories.group.on_group_remove.connect(self.update_on_group_remove)

    def _toggle_settings_widget(self):
        self.settings.toggle_widget_visibility()
        self.__frame_main.hide()

    def update_group_attributes(self, group_name: str, category: str):
        self.thumbnail.current_group = group_name
        self.thumbnail.current_category = category if category != "root" else None
        self.thumbnail.reset_attributes()

    def update_on_rename_category(self, group_name, old_category, new_category):
        self.thumbnail.current_group = group_name
        self.thumbnail.current_category = new_category

    def update_on_group_remove(self, group_removed: str):
        self.categories.tree.current_group = self.categories.group.current_group
        self.thumbnail.current_group = self.categories.group.current_group

    def on_change_group(self, group_name: str or None):
        """
        on change current group name

        :param group_name: group name
        :type group_name: str
        :return: None
        :rtype: None
        """
        if not group_name:
            self.categories.tree.setEnabled(False)
        else:
            self.categories.tree.setEnabled(True)
        self.categories.tree.root_item()

        self.categories.tree.current_group = group_name
        self.thumbnail.current_group = group_name
        self.thumbnail.reset_attributes()

    def _update_tree_group_attribute(self, group_name: str):
        """
        update current group attribute in treeWidget class.

        :param group_name: group name
        :type group_name: str
        :return: None
        :rtype: NOne
        """
        self.tree.current_group = group_name
