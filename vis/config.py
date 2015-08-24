"""
Represent the config
"""

import yaml

class Config(object):

    def load(self, file="config.yml"):
        # Look for a config file
        with open(file) as config_file:
            self.config = yaml.load(config_file)
