
import os
import json


class Settings:

    def __init__(self):

        self.pref = '{}/Documents/Ulaavi/preference/settings.json'.format(
            os.path.expanduser('~').replace('\\', '/')
        )

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
            dict_str = json.dumps({
                        "ffmpeg": "{}".format(ffmpeg),
                        "json": "{}".format(db),
                        "proxy": "{}".format(proxy),
                        "threads": "{}".format(thread),
                        "stay_top": "{}".format(stay_top),
                        "img_seq": "{}".format(img_seq)
                    }
            )
            file.write(dict_str)

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
        self.write_settings(
            '{}/ffmpeg/bin'.format(os.path.dirname(__file__).replace('\\', '/')),
            '{}/data.json'.format(os.path.dirname(self.pref).replace('\\', '/')),
            '{}/Documents/Ulaavi/Proxy'.format(os.path.expanduser('~').replace('\\', '/')),
            '4',
            True,
            True
        )
