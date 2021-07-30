import importlib.resources
import logging
from typing import Any, Dict

import toml

import shutterbug.config.resources as resources

__config = {}


# This is just a singleton updating a dicts, I don't see
# any reason to make this a class.
def init_configuration(**settings):

    # load runtime config
    for name, data in settings.items():
        logging.debug("Loaded configuration setting %s", name)
        update(name, data)
    __check_config()


def load_file_configuration():
    files = importlib.resources.files(resources)

    toml_resources = [x for x in files.iterdir() if x.suffix == ".toml"]
    # load user-defined config
    for f in toml_resources:
        data = toml.load(f)
        logging.debug("Loaded configuration file %s", f.stem)
        __config[f.stem] = data


def get(config_name: str) -> Dict:
    return __load_from_config(config_name=config_name, config_dict=__config)


def add(config_name: str, config_data: Any) -> bool:
    if config_name in __config.keys():
        logging.warning("Rejected attempt to overwrite configuration %s", config_name)
        return False
    else:
        __config[config_name] = config_data
        return True


def update(config_name: str, config_data: Any) -> bool:
    __config[config_name] = config_data
    if __config[config_name] == config_data:
        return True
    else:
        return False


def __load_from_config(config_name: str, config_dict: Dict) -> Any:
    try:
        return config_dict[config_name]
    except KeyError:
        logging.warning(
            "Unable to load configuration from %s, not found in configuration",
            config_name,
        )
        return None


def __check_config():
    uniform = get("uniform")
    mag_y_scale = get("mag_y_scale")
    diff_y_scale = get("diff_y_scale")
    if uniform is True and (mag_y_scale is not None or diff_y_scale is not None):
        logging.warning(
            "Manual y-axis scaling and uniform y-axis flag are both set, disabling uniform flag."
        )
        update("uniform", False)