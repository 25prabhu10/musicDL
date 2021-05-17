#!/usr/bin/env python
"""Module for setting up logging."""

import logging
import os
import platform
import sys
from logging.handlers import RotatingFileHandler

import appdirs

from musicDL.exceptions import LogPathDoesNotExistException

LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

LOG_FORMATS = {
    "DEBUG": "%(asctime)-15s - %(name)s - %(levelname)s: %(message)s",
    "INFO": "%(asctime)s: %(message)s",
    "WARNING": "%(name)s - %(levelname)s: %(message)s",
    "ERROR": "%(asctime)-15s - %(name)s - %(levelname)s: %(message)s",
    "CRITICAL": "%(asctime)-15s - %(name)s - %(levelname)s: %(message)s",
}


def configure_logger(log_level="DEBUG", debug_file=None, verbose=False):
    """Configure logging for musicDL.

    Set up logging to debug file with given level.
    If ``debug_file`` is given set up logging to file with DEBUG level.
    """
    STREAM_LOG_LEVEL = "INFO"

    # Set up 'musicDL' logger
    logger = logging.getLogger("musicDL")
    logger.setLevel(logging.DEBUG)

    # Remove all attached handlers, in case there was
    # a logger with using the name 'musicDL'
    del logger.handlers[:]

    # Create a file handler if a log file is provided
    if debug_file is None:
        # Get default log path if user dose not provide one
        user_log_dir = appdirs.user_log_dir()
        if not os.path.exists(user_log_dir):
            os.mkdir(user_log_dir)
        debug_file = os.path.join(user_log_dir, "musicDL.log")
    elif not os.path.exists(debug_file):
        raise LogPathDoesNotExistException(
            "Log file {} does not exist.".format(debug_file)
        )

    # Create a file handler if a log file is provided
    debug_formatter = logging.Formatter(LOG_FORMATS[log_level], "%Y-%m-%d %H:%M:%S")
    file_handler = RotatingFileHandler(debug_file, maxBytes=25000, backupCount=10)
    file_handler.setLevel(LOG_LEVELS[log_level])
    file_handler.setFormatter(debug_formatter)
    logger.addHandler(file_handler)

    # Setup stream logger
    if verbose:
        log_formatter = logging.Formatter(
            LOG_FORMATS[STREAM_LOG_LEVEL], "%Y-%m-%d %H:%M:%S"
        )
        stream_log_level = LOG_LEVELS[STREAM_LOG_LEVEL]

        # Create a stream handler
        stream_handler = logging.StreamHandler(stream=sys.stdout)
        stream_handler.setLevel(stream_log_level)
        stream_handler.setFormatter(log_formatter)
        logger.addHandler(stream_handler)

    # Log system info
    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"Platform: {platform.platform()}")

    return logger
