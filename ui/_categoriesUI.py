"""
This module defines a Categories class, which is a custom Qt widget for managing and displaying categories in a
hierarchical structure. It combines two sub-components: CategoriesGroup (for managing groups of categories) and
CategoriesTree (for displaying the hierarchical tree of categories).
"""

# -------------------------------- built-in Modules ----------------------------------
from typing import Optional

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets
except ModuleNotFoundError:
    from PySide6 import QtWidgets

# -------------------------------- Custom Modules ------------------------------------
from ui._categoriesGroup import CategoriesGroup
from ui._categoriesTree import CategoriesTree


class Categories(QtWidgets.QFrame):
    """
    A custom Qt widget for managing and displaying categories in a hierarchical structure.

    This widget combines a `CategoriesGroup` widget (for managing groups) and a `CategoriesTree` widget
    (for displaying the hierarchical tree of categories). It handles the interaction between the group
    and tree components, enabling or disabling the tree based on the selected group.

    :param parent: The parent widget. Defaults to None.
    :type parent: QWidget, optional
    """

    def __init__(self, parent=None):
        """
        Initializes the Categories widget.

        :param parent: The parent widget. Defaults to None.
        :type parent: QWidget, optional
        """
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
        """
        Sets up signal-slot connections between the group and tree widgets.

        Connects the `CategoriesGroup` signals (`on_group_change`, `on_group_new`, `on_group_remove`)
        to the appropriate slots in the `CategoriesTree` widget.
        """
        self.group.on_group_change.connect(self.on_change_group)
        self.group.on_group_new.connect(self._update_tree_group_attribute)
        self.group.on_group_remove.connect(
            lambda removedGrp: self._update_tree_group_attribute(self.group.current_group))

    def on_change_group(self, group: Optional[str]) -> None:
        """
        Handles changes to the selected group.

        Enables or disables the tree widget based on whether a group is selected.
        Updates the tree's root item and group attribute.

        :param group: The name of the selected group. If None or empty, the tree is disabled.
        :type group: str or None
        """
        if not group:
            self.tree.setEnabled(False)
        else:
            self.tree.setEnabled(True)
        self.tree.root_item()
        self._update_tree_group_attribute(group)

    def _update_tree_group_attribute(self, group: str) -> None:
        """
        Updates the `current_group` attribute of the tree widget.

        :param group: The name of the group to set as the current group in the tree.
        :type group: str
        """
        self.tree.current_group = group
