# -------------------------------- built-in Modules ----------------------------------
import re

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
    def __init__(self, selected_item, category_group, treeWidget):
        QtWidgets.QTreeWidgetItem.__init__(self, selected_item)
        self.__category_group = category_group
        self.__tree = treeWidget

    def setData(self, column, role, value):
        """
        set data

        :param column: column number
        :type column: int
        :param role: Qt Role
        :type role: int
        :param value: category
        :type value: str
        :return: None
        :rtype: None
        """
        if role in (QtCore.Qt.EditRole, QtCore.Qt.DisplayRole):
            _user_data = self.__tree.user_data(value, self)

            if not _user_data or self._is_category_exists(value, _user_data):
                self.setFlags(self.flags() & ~QtCore.Qt.ItemIsEditable)
                return

        QtWidgets.QTreeWidgetItem.setData(self, column, QtCore.Qt.EditRole, value)

    def _is_category_exists(self, category, tree_item_string: str):
        """
        check the item already exists or not

        :param category: category name (ex: data)
        :type category: str
        :param tree_item_string: tree user data (ex: root|data)
        :type tree_item_string: str
        :return:
        :rtype:
        """
        for item in self.__tree.findItems(category, QtCore.Qt.MatchRecursive, 0):
            if self.__tree.user_data(item.text(0), item) == tree_item_string:
                return True

        return False


class CategoriesTree(QtWidgets.QTreeWidget):
    """
    Categories
    """

    on_create = QtCore.Signal(str, str)
    on_remove = QtCore.Signal(str, str)
    on_change = QtCore.Signal(str, str)
    on_rename = QtCore.Signal(str, str, str)

    def __init__(self, parent=None) -> None:
        super().__init__()

        # declare datatypes
        self.__root_tree_item: QtWidgets.QTreeWidgetItem or None
        self.current_group: str or None

        self.__is_category_exists = False
        self.__category_to_rename = None
        self.__category_to_create = None
        self.__root_tree_item = None
        self.current_group = None

        self._set_widget_properties()
        self._widget_connections()

        self.root_item()

    def _set_widget_properties(self) -> None:
        """
        set QTreeWidget properties

        :return: None
        """
        self.setColumnCount(1)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.header().setVisible(False)
        self.header().setDefaultSectionSize(50)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._context_menu)

    def _widget_connections(self):
        self.currentItemChanged.connect(self._on_current_item_changed)
        self.itemChanged.connect(self._item_changed)

    def root_item(self):
        """
        load 'root' to tree and load categories as children.
        """
        self.clear()
        root = QtWidgets.QTreeWidgetItem(['root'])
        self.__root_tree_item = root
        self.addTopLevelItem(root)
        self.expandItem(root)
        self.setCurrentItem(root)

    def _context_menu(self, position) -> None:
        """
        context memu
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

    def user_data(self, category: str, current_item: QtWidgets.QTreeWidgetItem) -> str or None:
        """
        generate user data

        :param category: category name
        :type category: str
        :param current_item: category name
        :type current_item: str
        :return: user data (ex: root|data)
        :rtype: str or None
        """
        tree_items = []

        while True:
            tree_items.append(current_item.text(0))
            current_item = current_item.parent()
            if current_item is None:
                break

        if not tree_items:
            return

        tree_items = tree_items[::-1][:-1]
        tree_items.append(category)
        return '|'.join(tree_items)

    def _create_item(self):
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

        item = TreeWidgetItem(selected_item, self.current_group, self)
        self.setCurrentItem(item)
        item.setText(0, f"New_Item_{max_item}")
        item.setFlags(
            selected_item.flags() | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        # self.addTopLevelItem(item)
        self.currentItem().setExpanded(True)
        self.editItem(item, 0)
        self.__category_to_create = self.item_user_role

    def _rename_category(self):
        item = self.currentItem()
        if item.text(0).lower() == "root":
            return

        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
        self.editItem(item, 0)
        self.__category_to_rename = self.item_user_role

    def _item_changed(self):
        if self.__category_to_rename:
            self.on_rename.emit(self.current_group, self.__category_to_rename, self.item_user_role)
            self.on_change.emit(self.current_group, self.item_user_role)
            self.__category_to_rename = None

        if self.__category_to_create:
            self.on_create.emit(self.current_group, self.item_user_role)
            self.__category_to_create = None

    def _on_current_item_changed(self):
        """
        emit on_change signal on current change item.

        :return: None
        :rtype: None
        """
        _user_data = self.item_user_role
        if _user_data:
            self.on_change.emit(self.current_group, self.item_user_role)

    def is_category_item_exists(self, category, tree_item_string: str):
        """
        check the item already exists or not. if exist, return QTreeWidgetItem

        :param category: category name (ex: data)
        :type category: str
        :param tree_item_string: tree user data (ex: root|data)
        :type tree_item_string: str
        :return: is exist, QTreeWidgetItem or None
        :rtype: bool, QTreeWidgetItem or None
        """
        for item in self.findItems(category, QtCore.Qt.MatchRecursive, 0):
            if re.match(r"^%s(\|.*)?$" % self.user_data(category, item).replace('|', '\|'), tree_item_string):
                return True, item

        return False, None

    @property
    def current_item_text(self):
        return self.currentItem().text(0)

    def add_categories(self, categories: list):
        """
        add categories

        :param categories: category names
        :type categories: list
        :return: None
        :rtype: None
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

                item = TreeWidgetItem(_current_item, self.current_group, self)
                _user_data += f'|{category_name}'
                item.setText(0, category_name)
                _current_item.addChild(item)
                item.setFlags(
                    item.flags() | QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                _current_item = item

    @property
    def item_user_role(self):
        current_item = self.currentItem()
        if current_item:
            return self.user_data(self.current_item_text, current_item)

    def _delete_items(self):
        """
        delete item from UI and send signal of deleted item user data

        :return: None
        :rtype: None
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
