from PySide2 import QtWidgets, QtCore
from . import commonWidgets


class TreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, selected_item, category_group, treeWidget):
        QtWidgets.QTreeWidgetItem.__init__(self, selected_item)

        self.__category_group = category_group
        self.__tree = treeWidget
        self.setFlags(self.flags() | QtCore.Qt.ItemIsEditable)

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
            user_data = self._user_data(value)

            if not user_data:
                return

            is_exists = self._is_category_exists(value, user_data)
            if is_exists:
                return

            QtWidgets.QTreeWidgetItem.setData(self, column, QtCore.Qt.UserRole, user_data)

        QtWidgets.QTreeWidgetItem.setData(self, column, QtCore.Qt.EditRole, value)
        self.setFlags(self.flags() & ~QtCore.Qt.ItemIsEditable)

    def _user_data(self, category: str) -> str or None:
        """
        generate user data

        :param category: category name
        :type category: str
        :return: user data (ex: root|data)
        :rtype: str or None
        """
        tree_items = []
        current_item = self

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
            if item.data(0, QtCore.Qt.UserRole) == tree_item_string:
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

        self._root_item()
        self.findItems("me", QtCore.Qt.MatchContains | QtCore.Qt.UserRole, 0)

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
        self.customContextMenuRequested.connect(self.context_menu)

    def _widget_connections(self):
        self.currentItemChanged.connect(self._on_current_item_changed)
        self.itemChanged.connect(self._item_changed)

    def update_category_exists(self, is_exist: bool):
        self.__is_category_exists = is_exist

    def _root_item(self):
        """
        load 'root' to tree and load categories as children.
        """
        self.clear()
        root = QtWidgets.QTreeWidgetItem(['root'])
        self.__root_tree_item = root
        self.addTopLevelItem(root)
        self.expandItem(root)
        self.setCurrentItem(root)

    def context_menu(self, position) -> None:
        """
        context memu
        """
        add_action = QtWidgets.QAction("Add")
        rename_action = QtWidgets.QAction("Rename")
        delete_action = QtWidgets.QAction("Delete")

        menu = QtWidgets.QMenu(self)
        menu.addAction(add_action)
        menu.addAction(rename_action)
        menu.addSeparator()
        menu.addAction(delete_action)

        add_action.triggered.connect(self.create_item)
        rename_action.triggered.connect(self._rename_category)
        delete_action.triggered.connect(self._delete_items)

        menu.exec_(self.mapToGlobal(position))

    def create_item(self):
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
        self.addTopLevelItem(item)
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
        user_data = self.item_user_role
        if user_data:
            self.on_change.emit(self.current_group, self.item_user_role)

    @property
    def current_item_text(self):
        return self.currentItem().text(0)

    @property
    def item_user_role(self, column: int = 0):
        return self.currentItem().data(column, QtCore.Qt.UserRole)

    def _delete_items(self):
        """
        delete item from UI and send signal of deleted item user data

        :return: None
        :rtype: None
        """
        if self.currentItem().text(0).lower() == "root":
            return

        if not commonWidgets.popup_message('Delete Item(s)',
                                           'Are you sure want to delete item(s)?',
                                           msgType='question',
                                           parent=self):
            return

        current_item_user_data = self.currentItem().data(0, QtCore.Qt.UserRole)
        self.currentItem().takeChildren()
        self.currentItem().parent().removeChild(self.currentItem())

        self.on_remove.emit(self.current_group, current_item_user_data)
