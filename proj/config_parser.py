import yaml


class Config:
    def __init__(self, config_path):
        self.config = None
        # Assign config file location to class variable
        self.config_path = config_path

        # Call helper funcs
        self.load_config()

    def get(self, *args, default=None):
        current = self.config
        for arg in args:
            if arg not in current:
                return default
            current = current[arg]
        return current

    def load_config(self):
        # Can also be called by itself to reload config.
        with open(self.config_path) as config_file:
            self.config = yaml.safe_load(config_file)

    def change_config_path(self, config_path, reload=True):
        # Used to change which config the pointer points to.
        self.config_path = config_path

        if reload:
            self.load_config()
