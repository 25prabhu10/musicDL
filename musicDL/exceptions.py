#!/usr/bin/env python
"""All exceptions used in the Cookiecutter code base are defined here."""


class MusicDLException(Exception):
    """
    Base exception class.

    All musicDL-specific exceptions should subclass this class.
    """


class ConfigDoesNotExistException(MusicDLException):
    """
    Exception for missing config file.

    Raised when get_config() is passed a path to a config file, but no file
    is found at that path.
    """


class InvalidConfiguration(MusicDLException):
    """
    Exception for invalid configuration file.

    Raised if the global configuration file is not valid YAML or is
    badly constructed.
    """


class LogPathDoesNotExistException(MusicDLException):
    """
    Exception for missing log path.

    Raised when configure_logger() is passed a path to a log path, but no
    directory is found at that path.
    """
