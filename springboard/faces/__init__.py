

# BaseFace class for all your faces!
class BaseFace(object):

    # Make a tuple or getz the hoze again
    COMMANDS = ()
    EASTER_EGG = False

    def __init__(self):
        pass

    def help(self):
        raise NotImplemented

    def run_face(self, *args, **kwargs):
        raise NotImplemented

    def check_update(self):
        pass
