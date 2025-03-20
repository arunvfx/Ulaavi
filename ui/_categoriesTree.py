"""
This module provides a custom tree widget (`CategoriesTree`) and tree item (`TreeWidgetItem`) for managing hierarchical categories in a Qt-based application.

The `CategoriesTree` widget allows users to:
- Add, rename, and delete categories.
- Organize categories into a hierarchical structure (e.g., "root|data|images").
- Emit signals for category creation, renaming, deletion, and selection changes.

The `TreeWidgetItem` class extends `QTreeWidgetItem` to enforce data integrity when editing categories, ensuring that duplicate categories are not created.

Key Features:
- **Hierarchical Category Management**: Organize categories into nested structures.
- **Context Menu**: Provides options to add, rename, and delete categories.
- **Signals**: Emits signals for category changes, enabling integration with other parts of the application.
- **Data Integrity**: Prevents duplicate categories and ensures valid edits.

Dependencies:
- **PySide2/PySide6**: For Qt-based GUI functionality.
- **Custom Modules**: `commonWidgets` for utility functions like popup messages.

Example Use Cases:
- Organizing media files into hierarchical categories (e.g., "root|videos|2023").
- Managing tags or metadata in a structured way.
- Building a file or resource browser with nested categories.
"""

# -------------------------------- built-in Modules ----------------------------------
import re
from typing import Optional, List

# ------------------------------- ThirdParty Modules ---------------------------------
try:
    from PySide2 import QtWidgets, QtCore
    from PySide2.QtWidgets import QAction

except ModuleNotFoundError:
    from PySide6 import QtWidgets, QtCore, QtGui
    from PySide6.QtGui import QAction

# -------------------------------- Custom Modules ------------------------------------
from . import commonWidgets


class TreeWidgetItem(QtWidgets.QTreeWidgetItem):
    """
    Custom QTreeWidgetItem for handling category items in a tree structure.

    This class extends `QTreeWidgetItem` to provide additional functionality for
    managing categories and ensuring data integrity when editing items.

    Attributes:
        __tree (CategoriesTree): The parent tree widget.
    """

    def __init__(self, selected_item, treeWidget):
        """
        Initialize the TreeWidgetItem.

        :param selected_item: The parent item in the tree.
        :param treeWidget: The parent tree widget.
        """

        super().__init__(selected_item)
        self.__tree = treeWidget

    def setData(self, column: int, role: int, value: str) -> None:
        """
        Set data for the item, ensuring the category does not already exist.

        :param column: The column index.
        :type column: int
        :param role: The Qt role (e.g., QtCore.Qt.EditRole).
        :type role: int
        :param value: The new value for the item.
        :type value: str
        """
        if role in (QtCore.Qt.EditRole, QtCore.Qt.DisplayRole):
            _user_data = self.__tree.user_data(value, self)

            if not _user_data or self._is_category_exists(value, _user_data):
                self.setFlags(self.flags() & ~QtCore.Qt.ItemIsEditable)
                return

        super().setData(column, QtCore.Qt.EditRole, value)

    def _is_category_exists(self, category: str, tree_item_string: str) -> bool:
        """
        Check if a category already exists in the tree.

        :param category: The category name to check.
        :type category: str
        :param tree_item_string: The user data string for the category.
        :type tree_item_string: str
        :return: True if the category exists, False otherwise.
        :rtype: bool
        """
        for item in self.__tree.findItems(category, QtCore.Qt.MatchRecursive, 0):
            if self.__tree.user_data(item.text(0), item) == tree_item_string:
                return True

        return False


class CategoriesTree(QtWidgets.QTreeWidget):
    """
    A custom QTreeWidget for managing categories in a hierarchical structure.

    This widget allows users to add, rename, and delete categories, and emits
    signals for these actions.

    Signals:
        on_create (str, str): Emitted when a new category is created.
        on_remove (str, str): Emitted when a category is removed.
        on_change (str, str): Emitted when the current category changes.
        on_rename (str, str, str): Emitted when a category is renamed.
    """

    on_create = QtCore.Signal(str, str)
    on_remove = QtCore.Signal(str, str)
    on_change = QtCore.Signal(str, str)
    on_rename = QtCore.Signal(str, str, str)

    def __init__(self, parent=None) -> None:
        """
        Initialize the CategoriesTree.

        :param parent: The parent widget.
        """
        super().__init__(parent)

        self.current_group = None
        self.__root_tree_item = None
        self.__is_category_exists = False
        self.__category_to_rename = None
        self.__category_to_create = None

        self._set_widget_properties()
        self._widget_connections()
        self.root_item()

    def _set_widget_properties(self) -> None:
        """
        Set properties for the QTreeWidget.

        Configures the widget's appearance and behavior.
        """
        self.setColumnCount(1)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.header().setVisible(False)
        self.header().setDefaultSectionSize(50)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._context_menu)

    def _widget_connections(self) -> None:
        """
        Connect signals to slots for handling user interactions.
        """
        self.currentItemChanged.connect(self._on_current_item_changed)
        self.itemChanged.connect(self._item_changed)

    def root_item(self) -> None:
        """
        Initialize the tree with a root item and clear existing items.
        """
        self.clear()
        root = QtWidgets.QTreeWidgetItem(['root'])
        self.__root_tree_item = root
        self.addTopLevelItem(root)
        self.expandItem(root)
        self.setCurrentItem(root)

    def _context_menu(self, position) -> None:
        """
        Display a context menu for adding, renaming, or deleting categories.

        :param position: The position where the context menu should appear.
        """
        add_action = QAction("Add")
        rename_action = QAction("Rename")
        delete_action = QAction("Delete")

        menu = QtWidgets.QMenu(self)
        menu.addAction(add_action)
        menu.addAction(rename_action)
        menu.addSeparator()
        menu.addAction(delete_action)

        add_action.triggered.connect(self._create_item)
        rename_action.triggered.connect(self._rename_category)
        delete_action.triggered.connect(self._delete_items)

        menu.exec_(self.mapToGlobal(position))

    @staticmethod
    def user_data(category: str, current_item: QtWidgets.QTreeWidgetItem) -> Optional[str]:
        """
        Generate a user data string for a category.

        :param category: The category name.
        :type category: str
        :param current_item: The current tree item.
        :type current_item: QtWidgets.QTreeWidgetItem
        :return: A string representing the category's path (e.g., "root|data").
        :rtype: Optional[str]
        """
        tree_items = []

        while current_item:
            tree_items.append(current_item.text(0))
            current_item = current_item.parent()

        if not tree_items:
            return

        tree_items = tree_items[::-1][:-1]
        tree_items.append(category)
        return '|'.join(tree_items)

    def _create_item(self) -> None:
        """
        Create a new category item in the tree.
        """
        try:
            max_item = str(
                int(
                    max(
                        [item.text(0) for item in self.findItems(
                            "New_Item_", QtCore.Qt.MatchStartsWith | QtCore.Qt.MatchRecursive)]
                    ).split('_')[2]
                ) + 1
            ).zfill(2)
        except ValueError:
            max_item = str(1).zfill(2)

        selected_item = self.currentItem()

        item = TreeWidgetItem(selected_item, self)
        self.setCurrentItem(item)
        item.setText(0, f"New_Item_{max_item}")
        item.setFlags(
            selected_item.flags() | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.currentItem().setExpanded(True)
        self.editItem(item, 0)
        self.__category_to_create = self.item_user_role

    def _rename_category(self) -> None:
        """
        Rename the currently selected category.
        """
        item = self.currentItem()
        if item.text(0).lower() == "root":
            return

        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.editItem(item, 0)
        self.__category_to_rename = self.item_user_role

    def _item_changed(self) -> None:
        """
        Handle item changes and emit appropriate signals.
        """
        if self.__category_to_rename:
            self.on_rename.emit(self.current_group, self.__category_to_rename, self.item_user_role)
            self.on_change.emit(self.current_group, self.item_user_role)
            self.__category_to_rename = None

        if self.__category_to_create:
            self.on_create.emit(self.current_group, self.item_user_role)
            self.__category_to_create = None

    def _on_current_item_changed(self) -> None:
        """
        Emit a signal when the current item changes.
        """
        _user_data = self.item_user_role
        if _user_data:
            self.on_change.emit(self.current_group, self.item_user_role)

    def is_category_item_exists(self, category: str, tree_item_string: str) \
            -> tuple[bool, Optional[QtWidgets.QTreeWidgetItem]]:
        """
        Check if a category already exists in the tree.

        :param category: The category name to check.
        :type category: str
        :param tree_item_string: The user data string for the category.
        :type tree_item_string: str
        :return: A tuple containing a boolean indicating existence and the matching item (if found).
        :rtype: tuple[bool, Optional[QtWidgets.QTreeWidgetItem]]
        """
        for item in self.findItems(category, QtCore.Qt.MatchRecursive, 0):
            if re.match(r"^%s(\|.*)?$" % self.user_data(category, item).replace('|', '\|'), tree_item_string):
                return True, item

        return False, None

    @property
    def current_item_text(self) -> str:
        """
        Get the text of the currently selected item.

        :return: The text of the current item.
        :rtype: str
        """
        return self.currentItem().text(0)

    def add_categories(self, categories: List[str]) -> None:
        """
        Add multiple categories to the tree.

        :param categories: A list of category paths (e.g., ["root|data", "root|images"]).
        :type categories: list
        """
        for category in sorted(categories):
            _current_item = self.__root_tree_item
            category_items = category.split('|')
            _user_data = category_items[0]
            for category_name in category_items[1:]:
                if not category_name.strip():
                    continue

                is_exist, item = self.is_category_item_exists(category_name, category)
                if is_exist:
                    _current_item = item
                    _user_data += f'|{item.text(0)}'
                    continue

                item = TreeWidgetItem(_current_item, self)
                _user_data += f'|{category_name}'
                item.setText(0, category_name)
                _current_item.addChild(item)
                item.setFlags(
                    item.flags() | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                _current_item = item

    @property
    def item_user_role(self) -> Optional[str]:
        """
        Get the user data string for the currently selected item.

        :return: The user data string (e.g., "root|data").
        :rtype: Optional[str]
        """
        current_item = self.currentItem()
        if current_item:
            return self.user_data(self.current_item_text, current_item)

    def _delete_items(self) -> None:
        """
        Delete the currently selected item and emit a signal.
        """
        if self.current_item_text.lower() == "root":
            return

        if not commonWidgets.popup_message('Delete Item(s)',
                                           'Are you sure want to delete item(s)?',
                                           msgType='question',
                                           parent=self):
            return

        self.on_remove.emit(self.current_group, self.item_user_role)
        self.currentItem().takeChildren()
        self.currentItem().parent().removeChild(self.currentItem())
