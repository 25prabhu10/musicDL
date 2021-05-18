#!/usr/bin/env python
"""Global configuration handling."""

import copy
import os

import yaml

from musicDL.exceptions import ConfigDoesNotExistException, InvalidConfiguration

# Default configurations (HOW THINGS ARE)
DEFAULT_CONFIG = {
    "log-level": "DEBUG",
    "debug-file": None,
    "config-file": None,
    "verbose": False,
    "musicDL": {"quality": "HD"},
}


def merge_configs(default, overwrite):
    """Recursively update a dict with the key/value pair of another.

    Dict values that are dictionaries themselves will be updated, whilst
    preserving existing keys.
    """
    new_config = copy.deepcopy(default)

    for k, v in overwrite.items():
        # Make sure to preserve existing items in
        # nested dicts, for example `abbreviations`
        if isinstance(v, dict):
            new_config[k] = merge_configs(default.get(k, {}), v)
        else:
            new_config[k] = v

    return new_config


def get_config(config_path, cli_config):
    """Retrieve the config from the specified path, returning a config dict."""
    if config_path is None:
        return merge_configs(DEFAULT_CONFIG, cli_config)

    if not os.path.exists(config_path):
        raise ConfigDoesNotExistException(
            "Config file {} does not exist.".format(config_path)
        )

    with open(config_path, "r") as config_file:
        try:
            yaml_dict = yaml.safe_load(config_file)
        except yaml.YAMLError as e:
            raise InvalidConfiguration(
                "Unable to parse YAML file {}.".format(config_path)
            ) from e

    file_config_dict = merge_configs(DEFAULT_CONFIG, yaml_dict)

    return merge_configs(file_config_dict, cli_config)
