import functools
import os
import json

from abc import abstractmethod, ABC


class JsonHandler(ABC):
    """
    handle json file
    """

    @abstractmethod
    def __init__(self, json_file):
        self.json_file = json_file

        if os.path.isfile(self.json_file) is False:
            self.serialize(data={})

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


class PreferencesJson(JsonHandler):
    """
    preferences
    """

    def __init__(self, json_file) -> None:
        self.json_file = json_file
        JsonHandler.__init__(self, self.json_file)


class DataJson(JsonHandler):
    """
    DataJson handler
    """

    def __init__(self, json_file: str) -> None:
        self.json_file = json_file
        JsonHandler.__init__(self, self.json_file)

    def update_data_json(self, category_grp: str, category_items: str,
                         data: list) -> None:
        """
        serialize data to json

        :param category_grp:
        :param category_items:
        :param data:
        :return:
        """

        if not self.json_file:
            raise Exception('No Valid Json file found!, cannot serialize data!')

        data_to_update = {category_grp: {}}

        if category_items and not data:

            data_to_update = {category_grp: {category_items: []}}

        elif category_items and data:
            data_to_update = {category_grp: {category_items: data}}

        self.serialize(data_to_update)

    @functools.lru_cache(maxsize=None)
    def data(self) -> dict:
        """

        :param category_grp:
        :param category_items:
        :return:
        """
        if not self.json_file:
            raise Exception('No Valid Json file found!, cannot retrieve data')

        return self.deserialize()

    def data_by_key(self, category_grp_key, category_item_key=''):
        """
        Get category by key
        :param category_grp_key:
        :param category_item_key:
        :return:
        """
        category_grp = self.data().get(category_grp_key)

        if not category_item_key:
            return category_grp

        return category_grp.get(category_item_key)
