# -------------------------------- built-in Modules ----------------------------------
import configparser
import json
import os
import re
from abc import abstractmethod, ABC


# ------------------------------- ThirdParty Modules ---------------------------------

# -------------------------------- Custom Modules ------------------------------------


def make_directory(path: str) -> None:
    if not path:
        return

    if os.path.isdir(path) is False:
        os.makedirs(path)


class JsonHandler(ABC):
    """
    handle json file
    """

    @abstractmethod
    def __init__(self, json_file: str):
        self.json_file = json_file

        if not self.json_file:
            raise IOError('No valid json file assigned!')

    def serialize(self, data: dict) -> None:
        """
        Dump data into json
        :param data:
        :return:
        """
        make_directory(os.path.dirname(self.json_file))

        with open(self.json_file, 'w') as file_:
            json.dump(data, file_)

    def deserialize(self) -> dict:
        """
        :param json_file:
        :return:
        """
        with open(self.json_file, 'r') as file_:
            return json.load(file_)


class DataJson(JsonHandler):
    """
    DataJson handler
    """

    def __init__(self, json_file: str) -> None:
        JsonHandler.__init__(self, json_file)

        self.create_default_json()
        self.__data = self.deserialize()

    def create_default_json(self):
        if os.path.isfile(self.json_file) is False:
            self.serialize(data={"data": {}, "tags": []})

    def update_data(self,
                    category_grp: str = '',
                    category: str = '',
                    data: dict or None = None,
                    data_type: str = 'data',
                    tag: str = '',
                    source_files: list = None) -> None:
        """
        serialize data to json

        :param tag:
        :type tag:
        :param data_type:
        :type data_type:
        :param category_grp:
        :param category:
        :param data:
        :param source_files:
        :type source_files:
        :return:
        """

        if not self.json_file:
            raise Exception('No Valid Json file found!, cannot serialize data!')

        if data_type == 'data':
            if not category_grp:
                raise KeyError('"category_grp" is must for data type "data"!')

            if not category:
                self.__data[data_type][category_grp] = {}

            elif category and data and not tag:
                self.__data[data_type][category_grp][category].append(data)

            elif category and not data and not tag:
                self.__data[data_type][category_grp][category] = []

            elif category and source_files and tag:
                items = self.__data[data_type][category_grp][category]
                for index, item in enumerate(items):

                    for source_file in source_files:
                        if item['source'] != source_file or tag in item['tags']:
                            continue

                        item['tags'].append(tag)

        elif data_type == 'tags':
            if not tag:
                raise KeyError('Data type "tags" expects "tag" argument!')

            if tag not in self.__data['tags']:
                self.__data[data_type].append(tag)

        self.serialize(self.__data)

    def remove_data(self, group: str, category: str, source_files: list, tag: str = None):
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
                   category_grp: str = '',
                   category_key: str = '',
                   data_type: str = 'data',
                   tag: str = '') -> None:
        """
        remove group by 'category_grp' if 'category_key' does not exist and data_type=data.
        remove category by 'category_grp and key_to_remove' if 'category_key' exists and data_type=data.
        remove also child categories if remove_child is True, default is True
        remove tag if data_type=tags and tag exists.

        :param category_grp: group name
        :type category_grp: str
        :param category_key: category key
        :type category_key: str
        :param data_type: either data or tags
        :type data_type: str
        :param tag: tag element
        :type tag: str
        :return: None
        :rtype: None
        """

        if data_type == 'data':
            if not category_key:
                self.__data[data_type].pop(category_grp)
            else:
                item_to_pop = []

                for item_key, item_value in self.__data[data_type].get(category_grp).items():
                    if re.match(r"^%s(\|.*)?$" % category_key.replace('|', '\|'), item_key):
                        item_to_pop.append(item_key)

                for item in item_to_pop:
                    self.__data[data_type][category_grp].pop(item)
        elif data_type == 'tags':
            self.__data[data_type].remove(tag)

        self.serialize(self.__data)

    def update_key(self, group_name: str, category_to_replace: str, category_to_update: str) -> None:
        """
        rename key

        :param group_name: group name
        :type group_name: str1
        :param category_to_replace: previous category key
        :type category_to_replace: str
        :param category_to_update: renamed category key
        :type category_to_update: str
        :return: None
        :rtype: None
        """
        duplicate_data = {}

        for category, value in self.__data["data"][group_name].items():
            if re.match(r"^%s(\|.*)?$" % category_to_replace.replace('|', '\|'), category):
                renamed_category = category.replace(category_to_replace, category_to_update)
                duplicate_data[renamed_category] = value

            else:
                duplicate_data[category] = value

        self.__data["data"][group_name] = duplicate_data
        self.serialize(self.__data)
        self.refresh_data()

    def refresh_data(self, json_file: str = ''):
        if json_file:
            self.json_file = json_file

        self.create_default_json()

        self.__data = self.deserialize()

    @property
    def data(self) -> dict or None:
        """
        return data
        :return: data
        :rtype: dict
        """
        return self.__data.get('data')

    @property
    def tags(self) -> list:
        """
        return tags
        :return: tags
        :rtype: list[str]
        """
        return self.deserialize().get('tags')

    def data_by_key(self, category_grp_key, category_item_key=''):
        """
        Get category by key
        :param category_grp_key:
        :param category_item_key:
        :return:
        """
        category_grp = self.__data['data'].get(category_grp_key)

        if not category_item_key:
            return category_grp

        return category_grp.get(category_item_key)

    def groups(self):
        if not self.__data or not self.__data.get('data'):
            return
        for group_name, _ in self.__data['data'].items():
            yield group_name

    def category_items(self, category_group: str):
        if not self.__data or not self.__data.get('data'):
            return
        if self.__data['data'].get(category_group) is None:
            return

        for key, _ in self.__data['data'].get(category_group).items():
            yield key

    def is_category_item_exists(self, category_grp_key, category_item_key) -> bool:
        if self.__data['data'].get(category_grp_key):
            if self.__data['data'].get(category_grp_key).get(category_item_key) is not None:
                return True

        return False


class Preferences:

    def __init__(self):
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

    def _update_attributes(self):
        if not os.path.isfile(self.__preferences_file):
            self.write_default_values()

        preferences = self._read_preferences()

        self.proxy = preferences.get('proxy')
        self.data_file = preferences.get('data')
        self.thread_count = int(preferences.get('thread_count'))
        self.res_width = int(preferences.get('res_width'))
        self.res_height = int(preferences.get('res_height'))
        self.thumbnail = int(preferences.get('thumbnail'))

    def preferences(self):
        return {'proxy': self.proxy,
                'data': self.data_file,
                'thread_count': str(self.thread_count),
                'res_width': str(self.res_width),
                'res_height': str(self.res_height),
                'thumbnail': self.thumbnail}

    def update(self, data: dict):
        for key, value in data.items():
            self.config['SETTINGS'][key] = value

        self._write_preferences()
        self._update_attributes()

    def write_default_values(self):
        self.config['SETTINGS'] = self.default_values()
        self._write_preferences()
        self._update_attributes()

        make_directory(self.config['SETTINGS'].get('proxy'))
        make_directory(os.path.dirname(self.config['SETTINGS'].get('data')))

    def get(self, key: str):
        return self.config['SETTINGS'].get(key)

    def default_values(self):
        return {'proxy': f'{self.__rootPath}/proxy',
                'data': f'{self.__rootPath}/data.json',
                'thread_count': '4',
                'res_width': '520',
                'res_height': '300',
                'thumbnail': '1'}

    def _write_preferences(self):
        make_directory(os.path.dirname(self.__preferences_file))

        with open(self.__preferences_file, 'w') as configfile:
            self.config.write(configfile)

    def _read_preferences(self):
        self.config.read(self.__preferences_file)
        return self.config['SETTINGS']
