from xdg import BaseDirectory
import yaml


config = {}


def load_config(app, filename):
    config.clear()
    for filename in BaseDirectory.load_config_paths('pb', filename):
        with open(filename) as f:
            obj = yaml.load(f)
            config.update(obj)
    if app:
        app.config.from_mapping(config)
    return config
