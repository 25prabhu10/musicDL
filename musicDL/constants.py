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

# MP4 specific tags - see mutagen docs:
# http://mutagen.readthedocs.io/en/latest/api/mp4.html
M4A_TAG_PRESET = {
    "title": "\xa9nam",
    "titlesort": "sonm",
    "tracknumber": "trkn",
    "discnumber": "disk",
    "genre": "\xa9gen",
    "artist": "\xa9ART",
    "album": "\xa9alb",
    "albumartist": "aART",
    "date": "\xa9day",
    "originaldate": "purd",
    "copyright": "cprt",
    "writer": "\xa9wrt",
    "lyrics": "\xa9lyr",
    "podcast": "pcst",
    "comment": "\xa9cmt",  # usually used in podcasts
    "encoded": "\xa9too",
}

# MP3 specific tags - see mutagen docs
MP3_TAG_PRESET = {
    "title": "title",
    "titlesort": "titlesort",
    "tracknumber": "tracknumber",
    "discnumber": "discnumber",
    "genre": "genre",
    "artist": "artist",
    "album": "album",
    "albumartist": "albumartist",
    "date": "date",
    "originaldate": "originaldate",
    "copyright": "copyright",
    "writer": "composer",
    "lyrics": "lyrics",
    "podcast": "podcast",
    "comment": "comment",  # usually used in podcasts
    "encoded": "encodedby",
}
