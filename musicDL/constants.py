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

# Logging format
LOG_FORMAT = "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"

# Progress bar theme
progress_bar_theme = {
    "bar.back": "grey23",
    "bar.complete": "rgb(165,66,129)",
    "bar.finished": "rgb(114,156,31)",
    "bar.pulse": "rgb(165,66,129)",
    "general": "green",
    "nonimportant": "rgb(40,100,40)",
    "progress.data.speed": "red",
    "progress.description": "none",
    "progress.download": "green",
    "progress.filesize": "green",
    "progress.filesize.total": "green",
    "progress.percentage": "green",
    "progress.remaining": "rgb(40,100,40)",
}
