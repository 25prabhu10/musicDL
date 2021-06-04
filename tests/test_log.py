#!/usr/bin/env python
"""Collection of tests around log handling."""

import logging
from pathlib import Path

import pytest
from musicDL.log import configure_logger


def create_log_records():
    """Test function, creates log entries in expected stage of test."""
    musicDL_logger = logging.getLogger("musicDL")
    main = logging.getLogger("musicDL.main")

    musicDL_logger.info("Welcome to musicDL")
    musicDL_logger.debug("Song URL passed")
    main.info("Loading user config from home dir")
    main.debug("I don't know.")
    main.debug("I wanted to save the world.")
    main.error("Aw, snap! Something went wrong")
    musicDL_logger.debug("Successfully downloaded the music")


@pytest.fixture
def info_messages():
    """Fixture: That returns a list of test info messages."""
    return [
        "Welcome to musicDL",
        "Loading user config from home dir",
        "Aw, snap! Something went wrong",
    ]


@pytest.fixture
def debug_file(tmp_path):
    """Fixture: That returns debug file location for tests."""
    return tmp_path.joinpath("pytest-plugin.log")


@pytest.fixture
def info_logger_with_file(debug_file):
    """Fixture: That calls musicDL logger setup with `info` info level + `file`."""
    return configure_logger(log_level="INFO", debug_file=str(debug_file))


def test_debug_file_logging(caplog, info_logger_with_file, debug_file, info_messages):
    """
    Test that file handler logs use info format and level
    and save logs to file
    """

    [file_handler] = info_logger_with_file.handlers
    assert isinstance(file_handler, logging.FileHandler)
    assert file_handler.level == logging.INFO

    create_log_records()

    assert str(debug_file) == file_handler.baseFilename
    assert debug_file.exists()

    # Last line in the log file is an empty line
    with debug_file.open() as f:
        assert f.read().split("\n")[0].endswith(info_messages[0])


@pytest.fixture
def info_logger_with_default_file(tmpdir_factory):
    """
    Fixture: That calls musicDL logger setup with `info` info level
    + default log `file`.
    """

    # Use temp-log as default user log path
    tmp_dir = str(Path(tmpdir_factory.mktemp("temp-log"), "temp-log.log"))
    return configure_logger(log_level="INFO", debug_file=tmp_dir)


def test_default_debug_file_logging(
    caplog, info_logger_with_default_file, info_messages
):
    """Test that logging to default log file uses info format and level"""
    [file_handler] = info_logger_with_default_file.handlers
    assert isinstance(file_handler, logging.FileHandler)
    assert file_handler.level == logging.INFO

    debug_file = Path(file_handler.baseFilename)

    create_log_records()

    assert debug_file.exists()

    # Last line in the log file is an empty line
    with debug_file.open() as f:
        assert f.read().split("\n")[0].endswith(info_messages[0])
