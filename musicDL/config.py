#!/usr/bin/env python
"""Global configuration handling."""

import copy
import os

import yaml
from logzero import logger as log

from .exceptions import ConfigDoesNotExistException, InvalidConfiguration

# Default configurations (HOW THINGS ARE)
DEFAULT_CONFIG = {
    "music-downloader": {
        "track-quality": "HD",
        "cover-quality": "high",  # low:150x150px or high:500x500px
        "no-metadata": False,  # don't embed metadata
        "no-cover": False,  # don't embed cover image
        "no-lyrics": False,  # don't download and embed lyrics (split)
        "no-fallback-metadata": False,
        "output-ext": None,  # output file format: mp3, m4a, etc..
        # use avconv for conversion (otherwise defaults to ffmpeg)
        "avconv": False,
        "trim-silence": False,
        # "folder": internals.get_music_dir(),  # download-folder
        "file-format": "{track_name} - {album}",  # music file name format
        "no-spaces": False,  # file should contain space or not
        "overwrite": "prompt",  # what to do when file exists
        "write-to": None,  # save urls to thisfile
        "write-successful": None,
        "skip": None,  # skip if file already downloaded
        "search-format": "{artist} - {track_name} lyrics",
        "podcast": False,  # mention if its from podcast
        "auto-download": False,  # download the first result
        "dry-run": False,  # get list of songs
        "log-level": "DEBUG",  # default debug level
        "verbose": True,
    }
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


def get_config(config_path):
    """Retrieve the config from the specified path, returning a config dict."""
    if not os.path.exists(config_path):
        raise ConfigDoesNotExistException(
            "Config file {} does not exist.".format(config_path)
        )

    log.debug("config_path is %s", config_path)
    with open(config_path, "r") as config_file:
        try:
            yaml_dict = yaml.safe_load(config_file)
        except yaml.YAMLError as e:
            raise InvalidConfiguration(
                "Unable to parse YAML file {}.".format(config_path)
            ) from e

    config_dict = merge_configs(DEFAULT_CONFIG, yaml_dict)

    return config_dict
