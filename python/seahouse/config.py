import os
from configparser import SafeConfigParser

CONFIGURATION_DIR = os.path.realpath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'config')
)

CONFIGURATION_FILE = os.path.join(CONFIGURATION_DIR, 'seahouse.conf')
_config = None


def load_config(file=None):
    global _config

    files = [CONFIGURATION_FILE]
    if file is not None:
        files.insert(0, file)

    _config = SafeConfigParser()
    _config.read(files)

    return _config


def get_config():
    return _config
