import configparser
import json
import os
import re
from abc import abstractmethod, ABC
from pathlib import Path


def make_directory(path: Path) -> None:
    if not Path:
        return

    if path.is_dir() is False:
        path.mkdir(exist_ok=True)


class JsonHandler(ABC):
    """
    handle json file
    """

    @abstractmethod
    def __init__(self, json_file):
        self.json_file = Path(json_file)

        make_directory(self.json_file.parent)
        if os.path.isfile(self.json_file) is False:
            self.serialize(data={"data": {}, "tags": []})

    def serialize(self, data: dict) -> None:
        """
        Dump data into json
        :param data:
        :param json_file:
        :return:
        """
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
        self.data_file = json_file
        JsonHandler.__init__(self, self.data_file)

        self.__data = self.deserialize()

    def add_key(self,
                category_grp: str = '',
                category: str = '',
                data: dict or None = None,
                data_type: str = 'data',
                tag: str = '') -> None:
        """
        serialize data to json

        :param tag:
        :type tag:
        :param data_type:
        :type data_type:
        :param category_grp:
        :param category:
        :param data:
        :return:
        """

        if not self.data_file:
            raise Exception('No Valid Json file found!, cannot serialize data!')

        if data_type == 'data':
            if not category_grp:
                raise KeyError('"category_grp" is must for data type "data"!')

            if category_grp and not category:
                self.__data[data_type][category_grp] = {}

            elif category:
                if not data:
                    data = {}
                self.__data[data_type][category_grp][category] = data

        elif data_type == 'tags':
            if not tag:
                raise KeyError('Data type "tags" expects "tag" argument!')

            if tag not in self.__data['tags']:
                self.__data[data_type].append(tag)

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
        data = {"data": {group_name: {}}, "tags": self.__data.get('tags')}

        for category, value in self.__data["data"][group_name].items():
            if re.match(r"^%s(\|.*)?$" % category_to_replace.replace('|', '\|'), category) is None:
                data["data"][group_name][category] = value
                continue

            renamed_category = category.replace(category_to_replace, category_to_update)
            print(data)
            data["data"][group_name][renamed_category] = value

        self.serialize(data)

        self.refresh_data()

    def refresh_data(self):
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
        self.__rootPath = f'{Path.home()}/Documents/ulaavi'.replace('\\', '/')
        self.__preferences_file = Path(f'{self.__rootPath}/preferences.ini')

        self.proxy = None
        self.data_file = None
        self.thread_count = None
        self.res_width = None
        self.res_height = None
        self.thumbnail = None

        self._update_attributes()

    def update(self, data: dict):
        for key, value in data.items():
            self.config['SETTINGS'][key] = value

        self._write_preferences()
        self._update_attributes()

    def reset(self):
        self._default_values()
        self._write_preferences()
        make_directory(Path(self.config['SETTINGS'].get('proxy')))
        make_directory(Path(self.config['SETTINGS'].get('data')).parent)

    def get(self, key: str):
        return self.config['SETTINGS'].get(key)

    def _update_attributes(self):
        if not self.__preferences_file.is_file():
            self.reset()

        preferences = self._read_preferences()

        self.proxy = preferences.get('proxy')
        self.data_file = preferences.get('data')
        self.thread_count = int(preferences.get('thread_count'))
        self.res_width = int(preferences.get('res_width'))
        self.res_height = int(preferences.get('res_height'))
        self.thumbnail = int(preferences.get('thumbnail'))

    def _default_values(self):
        self.config['SETTINGS'] = {'proxy': f'{self.__rootPath}/proxy',
                                   'data': f'{self.__rootPath}/data.json',
                                   'thread_count': '4',
                                   'res_width': '520',
                                   'res_height': '300',
                                   'thumbnail': '1'}

    def _write_preferences(self):
        make_directory(self.__preferences_file.parent)

        with open(self.__preferences_file, 'w') as configfile:
            self.config.write(configfile)

    def _read_preferences(self):
        self.config.read(self.__preferences_file)
        return self.config['SETTINGS']


if __name__ == '__main__':
    p = Preferences()
    print(p.proxy)
    print(p.get('data'))
