#!/usr/bin/env python
"""Collection of tests around loading musicDL config."""

from pathlib import Path

import appdirs
import pytest

from musicDL.config import Config


def test_get_default_config():
    config_path = Path(appdirs.user_config_dir(), "musicDL", "config.json")
    log_file_path = Path(appdirs.user_log_dir(), "musicDL", "main.log")
    expected = {
        "quality": "HD",
        "output": ".",
        "only-tagging": False,
        "no-coverart": False,
        "no-lyrics": False,
        "no-tags": False,
        "save-lyrics": False,
        "backup": False,
        "output-format": "",
        "ffmpeg": "ffmpeg",
        "ignore-ffmpeg-version": False,
        "log-level": "DEBUG",
        "debug-file": str(log_file_path),
        "config-file": str(config_path),
        "verbose": False,
    }

    assert Config.get_default_config() == expected


def test_set_config():
    pass


# Arrange
@pytest.fixture(autouse=True)
def cli_options(request):
    """Fixture: That uses valid config path and CLI options"""
    config_file_path = "tests/test-config/valid-config.json"
    cli_options = {
        "quality": "low",
        "log-level": "INFO",
        "debug-file": "",
        "config-file": "",
        "verbose": True,
    }
    Config.set_config(config_file_path, cli_options)


@pytest.mark.parametrize(
    "option,expected",
    [("log-level", "INFO"), ("output", "."), ("verbose", True), ("backup", False)],
)
def test_get_config(option, expected):
    """Test valid config opened and rendered correctly."""
    # Act
    config_dict = Config.get_config(option)

    # Assert
    assert config_dict == expected
