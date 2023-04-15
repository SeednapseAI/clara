import os
import yaml
from mergedeep import merge

from .consts import CONFIG_PATH


defaults = {"llm": {"name": "gpt-3.5-turbo", "temperature": 0}}


config = defaults


def load_config():
    global config

    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as file:
            merge(config, yaml.load(file, Loader=yaml.Loader))


load_config()
