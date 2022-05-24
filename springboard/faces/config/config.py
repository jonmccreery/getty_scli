from springboard.faces import BaseFace
from springboard import CONFIG
from springboard import Settings
import argparse
import pickle
import os
import sys


class SBConfig(BaseFace):
    # Trailing comma mandatory for single value tuples because python.
    COMMANDS = ('config',)

    def __init__(self):
        super().__init__()
        self.version = os.path.join(os.path.dirname(__file__), '../version.txt')

    def help(self, parser):
        parser.print_help()
        exit()

    def run_face(self, *args):
        parser = argparse.ArgumentParser()
        parser.add_argument('command', choices=['set', 'print', 'help'],
                            help='set (set a key/value), print (show config)',
                            metavar='set|print|help')
        parser.add_argument('-k', '--key', help='The key you wish to set.')
        parser.add_argument('-v', '--value', help='The desired value for the key.')
        args = parser.parse_args(args[1:])
        if args.command == 'set':
            self.set_config(args)
        elif args.command == 'print':
            self.print_config()
        else:
            self.help(parser)

    def print_config(self):
        print("\nCurrent Springboard Settings: ")
        print("-" * 29)
        for key, value in sorted(CONFIG.items()):
            print("{}: {}".format(key, value))

    def set_config(self, args):
        # Create a new settings hash
        new_settings = {}
        if not args.key:
            print("You must supply a key and value to set.")
            exit
        elif not args.value:
            print("Clearing value for {}".format(args.key))
        else:
            new_settings[args.key] = args.value

        for key, value in CONFIG.items():
            if key in new_settings or key == args.key:
                pass
            else:
                new_settings[key] = value

        with open(Settings().config_file, 'wb') as settings:
            pickle.dump(new_settings, settings, pickle.HIGHEST_PROTOCOL)
