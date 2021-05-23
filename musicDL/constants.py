"""Global constants."""

from logging import CRITICAL, DEBUG, ERROR, INFO, WARNING

# Default configurations (HOW THINGS ARE)
DEFAULT_CONFIG = {
    "log-level": "DEBUG",
    "debug-file": "",
    "verbose": False,
    "musicDL": {"quality": "HD", "output": "."},
}

# Logging levels
LOG_LEVELS = {
    "DEBUG": DEBUG,
    "INFO": INFO,
    "WARNING": WARNING,
    "ERROR": ERROR,
    "CRITICAL": CRITICAL,
}

# Logging formats
LOG_FORMATS = {
    "DEBUG": "%(asctime)-15s - %(name)s - %(levelname)s: %(message)s",
    "INFO": "%(message)s",
    "WARNING": "%(name)s - %(levelname)s: %(message)s",
    "ERROR": "%(asctime)-15s - %(name)s - %(levelname)s: %(message)s",
    "CRITICAL": "%(asctime)-15s - %(name)s - %(levelname)s: %(message)s",
}
