import json
import os
from utils.settings import Settings


class Database:
    def __init__(self):
        settings = Settings()
        self.file = settings.load_settings()['json']

        # create data.json if doesn't exists
        if not os.path.isfile(self.file):
            data = json.dumps({}, indent=4)
            with open(self.file, 'w') as db:
                db.write(data)

    def ingest_to_json(self, dictionary, depth=None, group=None, selected_item=None):
        """
        ingest group/category
        """
        with open(self.file, 'r') as file:
            data = json.load(file)
        if depth == 1:
            data[group].update({dictionary:{}})
        if depth == 2:
            data[group][selected_item].update({dictionary: {}})
        if not depth:
            data.update(dictionary)
        with open(self.file, 'w') as file:
            json.dump(data, file, indent=4)

    def read_from_json(self):
        """
        read data.json
        :return: dict
        """
        with open(self.file, 'r') as file:
            data = json.load(file)
        return data

    def remove_category_from_json(self, group, depth=None, category=None, selected_sub=None):
        """
        pop group/category
        """
        with open(self.file, 'r') as file:
            data = json.load(file)
        if depth is None:
            data.pop(str(group))
        if depth == 1:
            del data[str(group)][str(category)]
        if depth == 2:
            del data[str(group)][str(category)][str(selected_sub)]
        with open(self.file, 'w') as file:
            json.dump(data, file, indent=4)
        if depth is None:
            return 'Removed %s from json' % group
        if depth == 1:
            return 'Removed %s from json' % category
        if depth == 2:
            return 'Removed %s from json' % selected_sub

    def update_category_to_json(self, updated_data, current_data, depth=None, group=None,
                                selected_sub=None):
        """
        update category
        """
        with open(self.file, 'r') as file:
            data = json.load(file)
        if depth == 1:
            data[group][updated_data] = data[group].pop(current_data)
        if depth == 2:
            data[group][selected_sub][updated_data] = data[group][selected_sub].pop(current_data)
        with open(self.file, 'w') as file:
            json.dump(data, file, indent=4)

    def update_items_into_json(self, item, current_category, top_category, group, key, fav=False):
        """
        update items to data.json
        """
        with open(self.file, 'r') as file:
            data = json.load(file)
        t = '{"%s": "%s"}' % (item, fav)
        data[group][top_category][current_category][key] = json.loads(t)
        with open(self.file, 'w') as file:
            json.dump(data, file, indent=4)

    def remove_item_from_json(self, current_category, top_category, group, key):
        """
        pop items from data.json
        """
        with open(self.file, 'r') as file:
            data = json.load(file)
        del data[group][top_category][current_category][key]
        with open(self.file, 'w') as file:
            json.dump(data, file, indent=4)


