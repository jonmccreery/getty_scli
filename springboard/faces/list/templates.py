from springboard.faces import BaseFace


class ListFace(BaseFace):

    # Make a tuple or getz the hoze again
    COMMANDS = ('list',)

    def __init__(self):
        pass

    def help(self):
        raise NotImplemented

    def run_face(self, *args):
        print('heyo: {}'.format(' '.join(args[0:])))

    def check_update(self):
        pass
