import importlib
import pkgutil
import inspect
import sys
import os

import springboard.faces


class EntryPoint(object):

    def __init__(self):
        # Load the faces for sho yo
        self.faces_loaded = {}
        # for _, modname, ispkg in pkgutil.iter_modules('{}.faces'.format(os.path.dirname(sys.modules[__name__].__file__))):
        for _, modname, ispkg in pkgutil.walk_packages(path=[os.path.join(os.path.dirname(__file__), 'faces')], prefix='springboard.faces.'):
            face = importlib.import_module('{}'.format(modname))
            for name, obj in inspect.getmembers(face):
                if inspect.isclass(obj) and issubclass(obj, springboard.faces.BaseFace):
                    if isinstance(obj.COMMANDS, tuple):
                        self.faces_loaded[obj.COMMANDS] = obj

    def run(self, *args):
        for commands in self.faces_loaded:
            for command in commands:
                if args and args[0] == command:
                    concrete_face = self.faces_loaded[commands]()
                    concrete_face.run_face(*args)
                    exit()

        # when you're here, you're broken
        print('No valid Springboard subcommand was found.')
        print('Here\'s a list of commands Springboard knows about:')
        print('\n')
        for commands in self.faces_loaded:
            if not self.faces_loaded[commands].EASTER_EGG:
                for command in commands:
                    if command:
                        print('    {}'.format(command))


def main():
    dothething = EntryPoint()
    dothething.run(*sys.argv[1:])
