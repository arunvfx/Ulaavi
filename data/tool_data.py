# -------------------------------- built-in Modules ----------------------------------
from typing import Generator

# ------------------------------- ThirdParty Modules ---------------------------------

# -------------------------------- Custom Modules ------------------------------------
from . import _handler


class Data:
    __instance = None

    # @staticmethod
    # def get_instance():
    #     if Data.__instance is None:
    #         Data.__instance = Data()
    #
    #     return Data.__instance

    def __init__(self):
        self.preferences = _handler.Preferences()
        self.data_obj = _handler.DataJson(self.preferences.data_file)
        self.__data = self.data_obj.data
        self.__tags = self.data_obj.tags

    def groups(self) -> Generator:
        """
        get group name from data.json

        :return: group names
        :rtype: Generator[str]
        """
        if not self.__data:
            return

        for group_name, _ in self.__data.items():
            yield group_name

    def add_group(self, group_name: str):
        """
        add group name to data.json

        :param group_name: group name
        :type group_name: str
        :return: None
        :rtype: None
        """
        self.data_obj.add_key(category_grp=group_name)

    def remove_group(self, group: str):
        self.data_obj.remove_key(category_grp=group)

    def add_category(self, group_name: str, category: str) -> None:
        """
        add category

        :param group_name: group name
        :type group_name: str
        :param category: category
        :type category: str
        :return: None
        :rtype: None
        """
        self.data_obj.add_key(category_grp=group_name, category=category)

    def rename_category(self, group_name: str, old_category: str, category: str) -> None:
        """
        rename category

        :param group_name: group name
        :type group_name: str
        :param old_category: previous category name
        :type old_category: str
        :param category: new category name
        :type category: str
        :return: None
        :rtype: None
        """
        self.data_obj.update_key(group_name, old_category, category)
        # self.__data[group_name][category] = self.__data[group_name].pop(old_category)

    def remove_category(self, group_name: str, category: str):
        """
        remove category

        :param group_name: group name
        :type group_name: str`
        :param category: category
        :type category: str
        :return: None
        :rtype: None
        """
        self.data_obj.remove_key(category_grp=group_name, category_key=category)

    def categories(self, group_name: str):
        """
        get categories of given group.

        :param group_name: group name
        :type group_name: str
        :return: categories
        :rtype: Generator
        """
        data = self.__data.get(group_name)
        if not data:
            return

        for category, _ in self.__data.get(group_name).items():
            yield category

    @property
    def tags(self):
        return self.__tags

    def add_tags(self, tag):
        self.data_obj.add_key(data_type='tags', tag=tag)

    def is_category_exists(self, group_name: str, category: str) -> bool:
        """
        check the given category already exists in the data.json.

        :param group_name: group name
        :type group_name: str
        :param category: category
        :type category: str
        :return: is exist or not
        :rtype: bool
        """
        return self.data_obj.is_category_item_exists(group_name, category)


if __name__ == '__main__':
    d = Data()
