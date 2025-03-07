from data import tool_data


class Operations:

    def __init__(self, ui):
        self.ui = ui
        self.data = tool_data.Data()

    def execute_on_startup(self):
        self.ui_add_group()
        self.ui_add_category()

    def ui_add_group(self):
        self.ui.categories.group.add_groups(self.data.groups())

    def ui_add_category(self):
        group = self.ui.categories.group.current_group
        if not group:
            return

        self.ui.categories.tree.add_categories(list(self.data.categories(group)))

    def on_delete(self, group: str, category: str):
        self.data.remove_category(group, category)

    def on_add_group(self, group: str):
        self.data.add_group(group)

    def on_remove_group(self, group: str):
        self.data.remove_group(group)

    def on_change_group(self, group: str):
        self.ui.categories.on_change_group(group_name=group)
        self.ui_add_category()

    def on_change_category(self, group: str, category: str):
        print('ON CHANGE CATEGORY: Group: ', group, '   Category: ', category)

    def on_add_category(self, group: str, category: str):
        self.data.add_category(group, category)

    def on_rename_category(self, group: str, old_category: str, new_category: str):
        self.data.rename_category(group, old_category, new_category)

    def on_open_settings(self):
        self.ui.settings.preferences_grp.update_pref_ui(self.data.preferences)

    def on_reset_preferences(self):
        self.ui.settings.preferences_grp.update_pref_ui(self.data.preferences.default_values())
