# -------------------------------- built-in Modules ----------------------------------
import os.path
from typing import Generator

# ------------------------------- ThirdParty Modules ---------------------------------

# -------------------------------- Custom Modules ------------------------------------
from . import _handler


class Data:

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
        self.data_obj.update_data(category_grp=group_name)

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
        self.data_obj.update_data(category_grp=group_name, category=category)

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

    def add_thumbnail_data(self, source_file, proxy_file, metadata, group, category):
        data = {'proxy': proxy_file, 'source': source_file, 'metadata': metadata, 'tags': []}
        self.data_obj.update_data(category_grp=group, category=category, data=data)
        return data

    def thumbnail_data(self, group: str, category: str, tag: str = None, search_string: str = None) -> list:
        if not tag and not search_string:
            return self.data_obj.data[group].get(category)

        elif tag and not search_string:
            return [data for data in self.data_obj.data[group].get(category) if tag in data['tags']]

        elif not tag and search_string:
            return [data for data in self.data_obj.data[group].get(category)
                    if search_string.lower() in os.path.basename(data['source']).lower()]

        else:
            return [data for data in self.data_obj.data[group].get(category)
                    if search_string.lower() in os.path.basename(data['source']).lower() and tag in data['tags']]

    def remove_data(self, group: str, category: str, source_files: list):
        self.data_obj.remove_data(group=group, category=category, source_files=source_files)

    @property
    def tags(self) -> list:
        """
        get tags

        :return: tags list
        :rtype: list
        """
        return self.__tags

    def create_tag(self, tag):
        self.data_obj.update_data(data_type='tags', tag=tag)
        self.__tags.append(tag)

    def add_tag(self, group: str, category: str, source_files: list, tag: str):
        self.data_obj.update_data(category_grp=group, category=category, source_files=source_files, tag=tag)

    def remove_tag(self, group: str, category: str, source_files: list, tag: str):
        self.data_obj.remove_data(group=group, category=category, source_files=source_files, tag=tag)

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

    def refresh(self):
        self.data_obj.json_file = self.preferences.data_file
        self.data_obj.refresh_data()
        self.__data = self.data_obj.data
