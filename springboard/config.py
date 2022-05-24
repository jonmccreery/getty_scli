import pickle
import os
import sys
import datetime
import os.path


class Settings(dict):
    def __init__(self):
        self.config_path = os.path.join(os.path.expanduser("~"), ".springboard")
        self.config_file = os.path.join(self.config_path, "settings.pickle")
        with open(os.path.join(os.path.dirname(__file__), 'version.txt'), 'r') as f:
            self['version'] = f.read()

    def __getattr__(self, name):
        return self[name]

    def get_config(self):
        if not os.path.isfile(self.config_file):
            print("Generating configuration file for Springboard CLI...")
            self.generate_config()

        with open(self.config_file, 'rb') as config:
            conf = pickle.load(config)

            del conf['version']
            self.update(conf)
            return self

    def generate_config(self):
        if not os.path.isdir(self.config_path):
            try:
                os.mkdir(self.config_path)
            except:
                print("Could not initialize configuration path: {}".format(self.config_path))

        try:
            version_tag = {'version': self['version']}
            print("Writing settings to {}".format(self.config_file))
            with open(self.config_file, 'wb') as config:
                pickle.dump(version_tag, config, pickle.HIGHEST_PROTOCOL)
        except Exception:
            print("Could not initialize configuration file: {}".format(self.config_file))
