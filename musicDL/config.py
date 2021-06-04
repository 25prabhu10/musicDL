#!/usr/bin/env python
"""Global configuration handling."""

import json
import sys
from pathlib import Path
from typing import Any  # For static type checking

import appdirs

from .utils import merge_dicts


class Config:
    __config: dict[str, Any] = {}

    @staticmethod
    def get_config(key: str) -> Any:
        """Returns app's configuration for the given key.

        Args:
            key: Name of the key whose value is required.

        Returns:
            App's configuration for the given key.
        """

        return Config.__config[key]

    @staticmethod
    def get_default_config() -> dict[str, Any]:
        """Returns app's default configuration."""

        config_path = Path(appdirs.user_config_dir(), "musicDL", "config.json")
        log_file_path = Path(appdirs.user_log_dir(), "musicDL", "main.log")

        config = {
            "quality": "HD",
            "output": ".",
            "only-tagging": False,
            "backup": False,
            "log-level": "DEBUG",
            "debug-file": str(log_file_path),
            "config-file": str(config_path),
            "verbose": False,
        }

        return config

    @staticmethod
    def set_config(config_path: str, cli_config: dict[str, Any]) -> None:
        """Set app's configurations.

        Merges default app configurations/user configurations
        with the CLI options and the result is used
        as the app's configurations.

        Args:
            config_path: Path of the config file.
            cli_config: The CLI options provided by the user.

        Raises:
            JSONDecodeError: An error occurred decoding config file.
        """

        DEFAULT_CONFIG = Config.get_default_config()

        if not config_path:
            config_path = DEFAULT_CONFIG["config-file"]

        _config_path = Path(config_path)

        # If config file dose not exist, then create the file
        # with default configs.
        if not _config_path.exists():
            _config_path.parent.mkdir(parents=True, exist_ok=True)
            with _config_path.open("w", encoding="UTF-8") as target:
                json.dump(DEFAULT_CONFIG, target)

            Config.__config = merge_dicts(DEFAULT_CONFIG, cli_config)
            return None

        with _config_path.open("r", encoding="UTF-8") as config_file:
            try:
                json_dict = json.loads(config_file.read())
            except json.JSONDecodeError as e:
                print(f"{e.msg}\nUnable to parse JSON file: {config_path}")
                sys.exit(3)

        # Merge user configuration with CLI options
        Config.__config = merge_dicts(json_dict, cli_config)
