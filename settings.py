
import os
import json


class Settings:
    def __init__(self):
        self.pref = os.path.expanduser('~').replace('\\', '/') + '/Documents/Ulaavi/preference/settings.json'

        # create root directory
        if not os.path.isdir(os.path.dirname(self.pref)):
            os.makedirs(os.path.dirname(self.pref))

        # create settings.json with default values
        if not os.path.isfile(self.pref):
            self.write_default_settings()

    def write_settings(self, ffmpeg, db, proxy, thread, stay_top, img_seq):
        """
        write default / user settings into settings.json
        """
        with open(self.pref, 'w') as file:
            file.write(
                '{"ffmpeg": "%s", "json": "%s", "proxy": "%s", "threads": "%s", "stay_top": "%s", "img_seq": "%s" }'
                % (ffmpeg, db, proxy, thread, stay_top, img_seq)
            )

    def load_settings(self):
        """
        open and return settings.json
        """
        with open(self.pref, 'r') as s:
            file = json.load(s)
        return file

    def write_default_settings(self):
        """
        default settings.
        """
        self.write_settings(os.path.dirname(__file__).replace('\\', '/') + '/ffmpeg/bin',
                            os.path.dirname(self.pref).replace('\\', '/') + '/data.json',
                            os.path.expanduser('~').replace('\\', '/') + '/Documents/Ulaavi/Proxy',
                            '4',
                            True,
                            True)
