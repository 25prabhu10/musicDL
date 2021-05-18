#!/usr/bin/env python
"""Collection of tests around loading musicDL config."""

import pytest
import yaml
from musicDL import config
from musicDL.exceptions import ConfigDoesNotExistException, InvalidConfiguration


def test_merge_configs():
    """Verify default and user config merged in expected way."""

    DEFAULT_CONFIG = {
        "log-level": "DEBUG",
        "debug-file": None,
        "config-file": None,
        "verbose": False,
        "musicDL": {
            "quality": "HD",
        },
    }

    user_config = {
        "debug-file": None,
        "config-file": "config.yml",
        "verbose": True,
        "musicDL": {
            "quality": "HD",
        },
    }

    expected_config = {
        "log-level": "DEBUG",
        "debug-file": None,
        "config-file": "config.yml",
        "verbose": True,
        "musicDL": {
            "quality": "HD",
        },
    }

    assert config.merge_configs(DEFAULT_CONFIG, user_config) == expected_config


# TODO: include tests for cli_config
def test_get_config():
    """Verify valid config opened and rendered correctly."""
    valid_config_path = "tests/test-config/valid-config.yaml"

    expected_conf = {
        "log-level": "DEBUG",
        "debug-file": None,
        "config-file": None,
        "verbose": False,
        "musicDL": {
            "quality": "HD",
        },
    }

    conf = config.get_config(valid_config_path, {})

    assert conf == expected_conf


def test_get_config_does_not_exist():
    """
    Check that `exceptions.ConfigDoesNotExistException` is raised when
    attempting to get a non-existent config file.
    """
    expected_error_msg = "Config file tests/not-exist.yaml does not exist."

    with pytest.raises(ConfigDoesNotExistException) as exc_info:
        config.get_config("tests/not-exist.yaml", {})
    assert str(exc_info.value) == expected_error_msg


def test_invalid_config():
    """
    An invalid config file should raise an `InvalidConfiguration`
    exception.
    """
    expected_error_msg = (
        "Unable to parse YAML file tests/test-config/invalid-config.yaml."
    )

    with pytest.raises(InvalidConfiguration) as exc_info:
        config.get_config("tests/test-config/invalid-config.yaml", {})
        assert expected_error_msg in str(exc_info.value)
        assert isinstance(exc_info.value.__cause__, yaml.YAMLError)
