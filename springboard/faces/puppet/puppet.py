from springboard.faces import BaseFace
class PuppetModule(BaseFace):
    # Trailing comma mandatory for single value tuples because python.
    COMMANDS = ('puppet',)

    def __init__(self):
        super().__init__()
        self.version = VERSION
        self.base_source  = os.path.dirname(os.path.realpath(__file__))
        if 'modulepath' in CONFIG:
            self.cwd=CONFIG['modulepath']
        else: self.cwd=os.getcwd()
        self.hiera_file = {}

    def help(self):
        pass

    def run_face(self, *args): 
        pass