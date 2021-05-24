#!/usr/bin/env python
"""Global configuration handling."""

import json
import sys
from typing import Any  # For static type checking

from .constants import DEFAULT_CONFIG
from .utils import merge_dicts


def get_config(config_path: str, cli_config: dict[str, Any]) -> dict[str, Any]:
    """Returns config after merging configs.

    Merges default configurations with user configurations
    and then merge the result with the CLI options.

    Args:
        config_path: Path of the config file.
        cli_config: A dict containing the CLI options provided by the user.

    Returns:
        A dict formed by merging all the default configurations,
        user defined file configurations, and user provided CLI options.

    Raises:
        JSONDecodeError: An error occurred decoding config file.
    """

    # Use default configurations if no config path is provided
    if not config_path:
        return merge_dicts(DEFAULT_CONFIG, cli_config)

    with open(config_path, "r") as config_file:
        try:
            json_dict = json.loads(config_file.read())
        except json.JSONDecodeError as e:
            print(f"{e.msg}\nUnable to parse JSON file: {config_path}")
            sys.exit(3)

    # Merge user file configuration with default configurations
    file_config_dict = merge_dicts(DEFAULT_CONFIG, json_dict)

    # Merge user configuration with CLI options
    return merge_dicts(file_config_dict, cli_config)
