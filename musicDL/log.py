#!/usr/bin/env python
"""Module for setting up logging."""

import logging
import os
import sys

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
    "DEBUG": "%(name)s - %(asctime)-15s - %(levelname)s: %(message)s",
    "INFO": "%(levelname)s: %(message)s",
    "WARNING": "%(levelname)s %(name)s: %(message)s",
    "ERROR": "%(levelname)s %(name)s: %(message)s",
    "CRITICAL": "%(levelname)s %(name)s: %(message)s",
}


def configure_logger(log_level="DEBUG", debug_file=None):
    """Configure logging for musicDL.

    Set up logging to debug file with given level.
    If ``debug_file`` is given set up logging to file with DEBUG level.
    """
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
    debug_formatter = logging.Formatter(LOG_FORMATS[log_level])
    file_handler = logging.FileHandler(debug_file)
    file_handler.setLevel(LOG_LEVELS[log_level])
    file_handler.setFormatter(debug_formatter)
    logger.addHandler(file_handler)

    # Setup stream logger
    log_formatter = logging.Formatter(LOG_FORMATS[log_level])
    log_level = LOG_LEVELS[log_level]

    # Create a stream handler
    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)

    return logger
