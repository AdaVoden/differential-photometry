"""Builds the ApplicationConfig object, writes configuration to a file and
returns the application data folder via the ConfigParser library"""

import configparser
from pathlib import Path
from shutterbug.config.application import ApplicationConfig, default_config, data_folder
from shutterbug.config.packages import DataConfig, PhotometryConfig, VariabilityConfig
import logging


def from_file(file: Path) -> ApplicationConfig:

    """Given a file, will generate an ApplicationConfig construct that contains all
    the configuration for the application that is present in the file. This
    generation will ignore all anomalous entries that the program does not
    understand and will only read entries that it does

    :param file: A path to a file
    :returns: ApplicationConfig object, containing all Shutterbug configuration in that file, if any

    """
    parser = configparser.ConfigParser()
    try:
        parser.read_file(str(file))
        return ApplicationConfig(
            _photometry=PhotometryConfig.fromconfigparser(parser),
            _variability=VariabilityConfig.fromconfigparser(parser),
            _data=DataConfig.fromconfigparser(parser),
        )
    except ValueError as e:
        logging.error(f"Failed to create application config with error {e}")
    except IOError as e:
        logging.error(f"Unable to open file for reading, received error {e}")
    finally:
        return default_config


def to_file(file: Path, config: ApplicationConfig) -> bool:

    """Writes the ApplicationConfig object to a specified file, regardless of type.
    Appends .ini to the end of the file name if not present

    :param file: Target file as a full URL
    :param config: ApplicationConfig object
    :returns: True if write was successful, False otherwise

    """
    try:
        if file.suffix != "ini":
            file.suffix = "ini"
        with open(file, "w") as f:
            parser = configparser.ConfigParser()
            parser.read_dict(config.all)
            parser.write(f, space_around_delimiters=True)
            return True
    except IOError as e:
        logging.error(f"Unable to write to file {file}, received error {e}")
        return False


def data_folder() -> Path:
    return data_folder()