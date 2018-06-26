import yaml


class Config:
    def __init__(self, config_file):
        # Assign config file location to class variable
        self.config_file = config_file

        # Call helper funcs
        self.load_config()

    def load_config(self):
        # Can also be called by itself to reload config.
        with open(self.config_file) as config_stream:
            self.config = yaml.load(config_stream)

    def change_config_file(self, config_file, reload=True):
        # Used to change which config the pointer points to.
        self.config_file = config_file

        if reload:
            self.load_config()
