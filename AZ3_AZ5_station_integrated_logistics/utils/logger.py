import os
import json
import logging.config

"""
def setup_logging(
    default_path='logging.json',
    default_level=logging.DEBUG,
    env_key='LOG_CFG'):


    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'r') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
        print("exists")
    else:
        logging.basicConfig(level=default_level)

"""

class Logger(object):

    @classmethod
    def setup_logging(cls, name):
        """Setup logging configuration

        """
        cls.logger = logging.getLogger(name)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        cls.logger.addHandler(handler)
        cls.logger.setLevel(logging.DEBUG)
        return cls.logger





