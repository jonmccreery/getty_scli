from springboard.faces import BaseFace


class FuzzyBunny(BaseFace):
    # Trailing comma mandatory for single value tuples because python.
    COMMANDS = ('fuzzybunny', 'help help help help help',)
    EASTER_EGG = True

    def __init__(self):
        super().__init__()

    def help(self):
        pass

    def run_face(self, *args):
        bunny = """
                            /|      __
                           / |   ,-~ /
                          Y :|  //  /
                          | jj /( .^
                          >-"~"-v"
                         /       Y
                        jo  o    |
                       ( ~T~     j
                        >._-' _./
                       /   "~"  |
                      Y     _,  |
                     /| ;-"~ _  l
                    / l/ ,-"~    \
                    \//\/      .- \
                     Y        /    Y*
                     l       I     !
                     ]\      _\    /"\
                    (" ~----( ~   Y.  )
            ~~~~~~~~~~~~~~~~~~~~~~~~~~
        """

        print("{}".format(bunny))
