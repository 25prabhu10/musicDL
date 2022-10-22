#!/usr/bin/env python
"""Module for setting up logging."""

import logging
import platform
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from . import __version__
from .constants import LOG_FORMAT, LOG_LEVELS


def configure_logger(log_level: str, debug_file: str) -> logging.Logger:
    """Configures logging for musicDL.

    Set up logging to debug file with given level.

    Args:
        log_level: Logging level for the debug file.
        debug_file: Path to the log file.

    Returns:
        An instance of ``logging.Logger``.
    """

    # Set up 'musicDL' logger
    logger = logging.getLogger("musicDL")
    logger.setLevel(logging.DEBUG)

    # Remove all attached handlers, in case there was
    # a logger with using the name 'musicDL'
    del logger.handlers[:]

    # Create a file handler if a log file is provided
    debug_file_path = Path(debug_file)
    if not debug_file_path.parent.exists():
        debug_file_path.parent.mkdir(parents=True, exist_ok=True)

    # Create a file handler
    debug_file = str(debug_file_path)
    debug_formatter = logging.Formatter(LOG_FORMAT, "%Y-%m-%d %H:%M:%S")
    file_handler = RotatingFileHandler(debug_file, maxBytes=25000, backupCount=10)
    file_handler.setLevel(LOG_LEVELS[log_level])
    file_handler.setFormatter(debug_formatter)
    logger.addHandler(file_handler)

    # Log system info
    python_version = sys.version.replace("\n", "")
    logger.debug(f"musicDL v{__version__} started")
    logger.debug(f"Python version: {python_version}")
    logger.debug(f"Platform: {platform.platform()}")

    return logger
