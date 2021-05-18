#!/usr/bin/env python
"""Collection of tests around log handling."""

import logging
from pathlib import Path

import pytest
from musicDL.log import configure_logger


def create_log_records():
    """Test function, create log entries in expected stage of test."""
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
    """Fixture: List of test info messages."""
    return [
        "Welcome to musicDL",
        "Loading user config from home dir",
        "Aw, snap! Something went wrong",
    ]


@pytest.fixture
def info_logger():
    """Fixture: Call musicDL logger setup in verbose mode."""
    return configure_logger(verbose=True)


def test_info_stdout_logging(caplog, info_logger, info_messages):
    """Test that stdout logs use info format and level."""
    [file_handler, stream_handler] = info_logger.handlers
    assert isinstance(stream_handler, logging.StreamHandler)
    assert stream_handler.level == logging.INFO

    create_log_records()

    stream_messages = [
        stream_handler.format(r)
        for r in caplog.records
        if r.levelno >= stream_handler.level
    ]

    assert stream_messages == info_messages


@pytest.fixture
def debug_file(tmp_path):
    """Fixture: Generate debug file location for tests."""
    return tmp_path.joinpath("pytest-plugin.log")


@pytest.fixture
def info_logger_with_file(debug_file):
    """Fixture: Call musicDL logger setup with `info` info level + `file`."""
    return configure_logger(log_level="INFO", debug_file=str(debug_file))


def test_debug_file_logging(caplog, info_logger_with_file, debug_file, info_messages):
    """Test that file handler logs use info format and level \
        and save logs to file"""
    [file_handler] = info_logger_with_file.handlers
    assert isinstance(file_handler, logging.FileHandler)
    assert file_handler.level == logging.INFO

    create_log_records()

    assert str(debug_file) == file_handler.baseFilename
    assert debug_file.exists()

    # Last line in the log file is an empty line
    with debug_file.open() as f:
        assert f.read().split("\n") == info_messages + [""]


@pytest.fixture
def info_logger_with_file_and_stream(debug_file):
    """Fixture: Call musicDL logger setup with `info` info level + `file`, \
        and stdout logs."""
    return configure_logger(log_level="INFO", debug_file=str(debug_file), verbose=True)


def test_debug_file_and_stream_logging(
    caplog, info_logger_with_file_and_stream, debug_file, info_messages
):
    """Test that logging to stdout and file uses info format and level."""
    [file_handler, stream_handler] = info_logger_with_file_and_stream.handlers
    assert isinstance(file_handler, logging.FileHandler)
    assert isinstance(stream_handler, logging.StreamHandler)
    assert stream_handler.level == logging.INFO
    assert file_handler.level == logging.INFO

    create_log_records()

    stream_messages = [
        stream_handler.format(r)
        for r in caplog.records
        if r.levelno >= stream_handler.level
    ]

    assert stream_messages == info_messages

    assert debug_file.exists()

    # Last line in the log file is an empty line
    with debug_file.open() as f:
        assert f.read().split("\n") == info_messages + [""]


@pytest.fixture
def info_logger_with_default_file(mocker, tmpdir_factory):
    """Fixture: Call musicDL logger setup with `info` info level \
        + default log `file`."""
    # Use temp-log as default user log path
    tmp_dir = str(Path(tmpdir_factory.mktemp("temp-log"), "temp-log"))

    mocker.patch("musicDL.log.appdirs.user_log_dir", return_value=tmp_dir)
    return configure_logger(log_level="INFO", debug_file=None)


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
        assert f.read().split("\n") == info_messages + [""]
