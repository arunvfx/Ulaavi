# -------------------------------- built-in Modules ----------------------------------

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets
except ModuleNotFoundError:
    from PySide6 import QtWidgets

# -------------------------------- Custom Modules ------------------------------------
from ui._categoriesGroup import CategoriesGroup
from ui._categoriesTree import CategoriesTree


class Categories(QtWidgets.QFrame):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.group = CategoriesGroup()
        self.tree = CategoriesTree()

        self.__main_layout = QtWidgets.QVBoxLayout(self)
        self.__main_layout.addWidget(self.group)
        self.__main_layout.addWidget(self.tree)
        self.__main_layout.setContentsMargins(9, 0, 0, 0)

        self._set_widget_connections()
        self.on_change_group('')

    def _set_widget_connections(self) -> None:
        self.group.on_group_change.connect(self.on_change_group)
        self.group.on_group_new.connect(self._update_tree_group_attribute)
        self.group.on_group_remove.connect(
            lambda removedGrp: self._update_tree_group_attribute(self.group.current_group))

    def on_change_group(self, group_name: str or None):
        """
        on change current group name

        :param group_name: group name
        :type group_name: str
        :return: None
        :rtype: None
        """
        if not group_name:
            self.tree.setEnabled(False)
        else:
            self.tree.setEnabled(True)
        self.tree.root_item()
        self._update_tree_group_attribute(group_name)

    def _update_tree_group_attribute(self, group_name: str):
        """
        update current group attribute in treeWidget class.

        :param group_name: group name
        :type group_name: str
        :return: None
        :rtype: NOne
        """
        self.tree.current_group = group_name
