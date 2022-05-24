# Current version of the Springboard CLI
from springboard.config import Settings
# import springboard.faces
# from springboard.config import SpringboardConfig
CONFIG = Settings().get_config()
VERSION = CONFIG['version']
