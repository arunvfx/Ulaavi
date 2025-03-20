"""
Summary:

This module provides utilities for managing JSON data and application preferences. It includes two main classes:
JsonHandler:
    An abstract base class for handling JSON files.
    Provides methods for serializing and deserializing JSON data.
    Subclasses must implement the __init__ method.

DataJson:
    Extends JsonHandler to manage JSON data organized into groups, categories, and tags.
    Provides methods to update, remove, and query data.
    Supports operations like adding/removing groups, categories, and tags.

Preferences:
    Manages application settings stored in a .ini file.
    Provides methods to read, update, and write preferences.
    Sets default values if the preferences file does not exist.
"""

# -------------------------------- built-in Modules ----------------------------------
import configparser
import json
import os
import re
from abc import abstractmethod, ABC
from typing import Dict, Optional, List, Union, Generator

# ------------------------------- ThirdParty Modules ---------------------------------

# -------------------------------- Custom Modules ------------------------------------
import _utilities


class JsonHandler(ABC):
    """
    Abstract base class for handling JSON files.

    This class provides methods for serializing and deserializing JSON data.
    Subclasses must implement the `__init__` method.

    Attributes:
        json_file (str): Path to the JSON file.
    """

    @abstractmethod
    def __init__(self, json_file: str):
        """
        Initialize the JsonHandler.

        :param json_file: Path to the JSON file.
        :type json_file: str
        :raises IOError: If no valid JSON file is provided.
        """
        self.json_file = json_file

        if not self.json_file:
            raise IOError('No valid json file assigned!')

    def serialize(self, data: Dict) -> None:
        """
        Serialize data into the JSON file.

        :param data: Data to serialize.
        :type data: Dict
        """
        _utilities.make_directory(self.json_file)

        with open(self.json_file, 'w') as file_:
            json.dump(data, file_)

    def deserialize(self) -> Dict:
        """
        Deserialize data from the JSON file.

        :return: Deserialized data.
        :rtype: Dict
        """
        with open(self.json_file, 'r') as file_:
            return json.load(file_)


class DataJson(JsonHandler):
    """
    Handler for managing JSON data with a specific structure.

    This class extends `JsonHandler` to manage JSON data organized into groups,
    categories, and tags. It provides methods to update, remove, and query data.

    Attributes:
        __data (Dict): Internal data structure for storing JSON data.
    """

    def __init__(self, json_file: str) -> None:
        """
        Initialize the DataJson handler.

        :param json_file: Path to the JSON file.
        :type json_file: str
        """
        super().__init__(json_file)

        self.create_default_json()
        self.__data = self.deserialize()

    def create_default_json(self) -> None:
        """
        Create a default JSON structure if the file does not exist.

        The default structure includes an empty "data" dictionary and an empty "tags" list.
        """
        if not os.path.isfile(self.json_file):
            self.serialize(data={"data": {}, "tags": []})

    def update_data(self,
                    group: str = '',
                    category: str = '',
                    data: Optional[Dict] = None,
                    data_type: str = 'data',
                    tag: str = '',
                    source_files: Optional[List[str]] = None) -> None:
        """
        Update data in the JSON file.

        :param group: Group name.
        :type group: str
        :param category: Category name.
        :type category: str
        :param data: Data to add.
        :type data: Optional[Dict]
        :param data_type: Type of data ('data' or 'tags').
        :type data_type: str
        :param tag: Tag to add.
        :type tag: str
        :param source_files: List of source files.
        :type source_files: Optional[List[str]]
        :raises Exception: If no valid JSON file is found.
        :raises KeyError: If required arguments are missing.
        """

        if not self.json_file:
            raise Exception('No valid JSON file found!, Cannot serialize data!')

        if data_type == 'data':
            if not group:
                raise KeyError('"group" is must for data type "data"!')

            if not category:
                self.__data[data_type][group] = {}

            elif category and data and not tag:
                self.__data[data_type][group][category].append(data)

            elif category and not data and not tag:
                self.__data[data_type][group][category] = []

            elif category and source_files and tag:
                for item in self.__data[data_type][group][category]:

                    if item['source'] in source_files and tag not in item['tags']:
                        item['tags'].append(tag)

        elif data_type == 'tags' and tag:
            if tag not in self.__data['tags']:
                self.__data['tags'].append(tag)

        self.serialize(self.__data)

    def remove_data(self, group: str, category: str, source_files: list, tag: str = None) -> None:
        """
        Remove data from the JSON file.

        :param group: Group name.
        :type group: str
        :param category: Category name.
        :type category: str
        :param source_files: List of source files.
        :type source_files: List[str]
        :param tag: Tag to remove.
        :type tag: Optional[str]
        """
        items = []

        for data in self.__data['data'][group][category]:
            if data.get('source') in source_files and tag is None:
                continue

            if tag and tag in data['tags']:
                data['tags'].remove(tag)
                items.append(data)
                continue

            items.append(data)

        self.__data['data'][group][category] = items
        self.serialize(self.__data)

    def remove_key(self,
                   group: str = '',
                   category: str = '',
                   data_type: str = 'data',
                   tag: str = '') -> None:
        """
        Remove a key from the JSON data.

        :param group: Group name.
        :type group: str
        :param category: Category key.
        :type category: str
        :param data_type: Type of data ('data' or 'tags').
        :type data_type: str
        :param tag: Tag to remove.
        :type tag: str
        """

        if data_type == 'data':
            if not category:
                self.__data[data_type].pop(group)
            else:
                for item_key in list(self.__data[data_type].get(group).keys()):
                    if re.match(rf"^%s(\|.*)?$" % category.replace('|', '\|'), item_key):
                        self.__data[data_type][group].pop(item_key)

        elif data_type == 'tags' and tag in self.__data['tags']:
            self.__data['tags'].remove(tag)

        self.serialize(self.__data)

    def update_key(self, group: str, category_to_replace: str, category_to_update: str) -> None:
        """
        Update a key in the JSON data.

        :param group: Group name.
        :type group: str
        :param category_to_replace: Category key to replace.
        :type category_to_replace: str
        :param category_to_update: New category key.
        :type category_to_update: str
        """
        duplicate_data = {}

        for category, value in self.__data["data"][group].items():
            renamed_category = re.sub(rf"^%s(\|.*)?$" % category_to_replace.replace('|', '\|'), category_to_update,
                                      category)
            # renamed_category = category.replace(category_to_replace, category_to_update)
            duplicate_data[renamed_category] = value

        self.__data["data"][group] = duplicate_data
        self.serialize(self.__data)
        self.refresh_data()

    def refresh_data(self, json_file: str = '') -> None:
        """
        Refresh the data from the JSON file.

        :param json_file: Path to the JSON file.
        :type json_file: str
        """
        if json_file:
            self.json_file = json_file

        self.create_default_json()
        self.__data = self.deserialize()

    @property
    def data(self) -> dict or None:
        """
        Get the data from the JSON file.

        :return: Data from the JSON file.
        :rtype: Optional[Dict]
        """
        return self.__data.get('data')

    @property
    def tags(self) -> list:
        """
        Get the tags from the JSON file.

        :return: List of tags.
        :rtype: List[str]
        """
        return self.deserialize().get('tags')

    def data_by_key(self, group: str, category: str = '') -> Union[Dict, List]:
        """
        Get data by category group and item key.

        :param group: Category group key.
        :type group: str
        :param category: Category item key.
        :type category: str
        :return: Data for the specified keys.
        :rtype: Union[Dict, List]
        """
        category_grp = self.__data['data'].get(group, {})

        return category_grp.get(category) if category else category_grp

    def is_category_item_exists(self, group: str, category: str) -> bool:
        """
        Check if a category item exists.

        :param group: Category group key.
        :type group: str
        :param category: Category item key.
        :type category: str
        :return: True if the item exists, False otherwise.
        :rtype: bool
        """
        return bool(self.__data['data'].get(group, {}).get(category))


class Preferences:
    """
    Handler for managing application preferences.

    This class manages application settings stored in a `.ini` file. It provides methods to read, update,
    and write preferences, as well as set default values if the preferences file does not exist.

    Attributes:
        config (configparser.ConfigParser): Parser for reading and writing `.ini` files.
        __rootPath (str): Root directory for storing preferences and related files.
        __preferences_file (str): Path to the preferences file.
        proxy (str): Path to the proxy directory.
        data_file (str): Path to the data file.
        thread_count (int): Number of threads for processing.
        res_width (int): Default resolution width.
        res_height (int): Default resolution height.
        thumbnail (int): Thumbnail setting (0 or 1).
    """
    __slots__ = ('config',
                 '__rootPath',
                 '__preferences_file',
                 'proxy', 'data_file',
                 'thread_count',
                 'res_width',
                 'res_height',
                 'thumbnail')

    def __init__(self):
        """
        Initialize the Preferences handler.

        Sets up the preferences file path and updates attributes from the file.
        If the file does not exist, default values are written.
        """
        self.config = configparser.ConfigParser()
        self.__rootPath = f'{os.path.expanduser("~")}/Documents/ulaavi'.replace('\\', '/')
        self.__preferences_file = f'{self.__rootPath}/preferences.ini'

        self.proxy = None
        self.data_file = None
        self.thread_count = None
        self.res_width = None
        self.res_height = None
        self.thumbnail = None

        self._update_attributes()

    def _update_attributes(self) -> None:
        """
        Update attributes from the preferences file.

        Reads the preferences file and updates the instance attributes.
        If the file does not exist, default values are written.
        """
        if not os.path.isfile(self.__preferences_file):
            self.write_default_values()

        preferences = self._read_settings()

        self.proxy = preferences.get('proxy')
        self.data_file = preferences.get('data')
        self.thread_count = int(preferences.get('thread_count'))
        self.res_width = int(preferences.get('res_width'))
        self.res_height = int(preferences.get('res_height'))
        self.thumbnail = int(preferences.get('thumbnail'))

    def preferences(self) -> Dict[str, str]:
        """
        Get all preferences as a dictionary.

        :return: Dictionary containing all preferences.
        :rtype: Dict[str, str]
        """
        return {'proxy': self.proxy,
                'data': self.data_file,
                'thread_count': str(self.thread_count),
                'res_width': str(self.res_width),
                'res_height': str(self.res_height),
                'thumbnail': self.thumbnail}

    def update(self, data: Dict[str, str]) -> None:
        """
        Update preferences with the provided data.

        :param data: Dictionary of preferences to update.
        :type data: Dict[str, str]
        """

        for key, value in data.items():
            self.config['SETTINGS'][key] = value

        self._write_preferences()
        self._update_attributes()

    def write_default_values(self) -> None:
        """
        Write default values to the preferences file.

        Creates the preferences file with default values if it does not exist.
        Also ensures the necessary directories are created.
        """
        self.config['SETTINGS'] = self.default_values()
        self._write_preferences()
        self._update_attributes()

        _utilities.make_directory(self.config['SETTINGS'].get('proxy'))
        _utilities.make_directory(self.config['SETTINGS'].get('data'))

    def get(self, key: str) -> Optional[str]:
        """
        Get a preference value by key.

        :param key: The key of the preference to retrieve.
        :type key: str
        :return: The value of the preference, or None if the key does not exist.
        :rtype: Optional[str]
        """
        return self.config['SETTINGS'].get(key)

    def default_values(self) -> Dict[str, str]:
        """
        Get default preference values.

        :return: Dictionary containing default preference values.
        :rtype: Dict[str, str]
        """
        return {'proxy': f'{self.__rootPath}/proxy',
                'data': f'{self.__rootPath}/data.json',
                'thread_count': '4',
                'res_width': '520',
                'res_height': '300',
                'thumbnail': '1'}

    def _write_preferences(self) -> None:
        """
        Write preferences to the file.

        Ensures the directory exists and writes the current configuration to the preferences file.
        """
        _utilities.make_directory(self.__preferences_file)

        with open(self.__preferences_file, 'w') as configfile:
            self.config.write(configfile)

    def _read_settings(self) -> configparser.SectionProxy:
        """
        Read preferences from the file and return "SETTINGS" section.

        :return: The 'SETTINGS' section of the preferences file.
        :rtype: configparser.SectionProxy
        """
        self.config.read(self.__preferences_file)
        return self.config['SETTINGS']
