#!/usr/bin/env python
"""Main `musicDL` CLI."""

import logging
import os
import sys
from datetime import date

import click  # Creates beautiful command line interface

from . import __version__
from .config import Config
from .log import configure_logger
from .main import musicDL

logger = logging.getLogger(__name__)


def version_msg() -> str:
    """Returns a formated string containing the musicDL package version,
    location of the package, Python version, and the current year.

    Returns:
        The musicDL version, location, Pathon version, current year.

        ``musicDL 0.3.3 from musicDL (Python 3.9) (c) 2021``
    """

    # Python version
    python_version = sys.version[:3]
    # Location of the module
    location = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # Current year
    year = date.today().year
    # Formated message
    message = "musicDL %(version)s from {} (Python {}) (c) {}"
    return message.format(location, python_version, year)


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(__version__, "--version", message=version_msg())
@click.argument("request", default=None, required=True, type=click.STRING)
@click.option(
    "-q",
    "--quality",
    default="hd",
    show_default=True,
    type=click.Choice(["low", "medium", "high", "hd"], case_sensitive=False),
    metavar="",
    help="Audio Quality: low:96kbps, medium:128kbps, high:160kbps, or hd:320kbps",
)
@click.option(
    "-o",
    "--output",
    default=".",
    show_default=True,
    type=click.Path(exists=True, file_okay=False),
    metavar="",
    help="Output directory path",
)
@click.option(
    "--only-tagging",
    is_flag=True,
    help="No downloading, only Embed tags into existing files.",
)
@click.option(
    "--no-lyrics",
    is_flag=True,
    help="Don't fetch lyrics.",
)
@click.option(
    "--no-coverart",
    is_flag=True,
    help="Don't embed cover art.",
)
@click.option(
    "--no-tags",
    is_flag=True,
    help="Don't embed tags.",
)
@click.option(
    "--save-lyrics",
    is_flag=True,
    help="Save lyrics as text files in the same output path.",
)
@click.option(
    "--backup",
    is_flag=True,
    help="Backup the tracking file.",
)
@click.option(
    "--log-level",
    default="DEBUG",
    show_default=True,
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    metavar="",
    help="Set stream logging to verbose",
)
@click.option(
    "--debug-file",
    default="",
    type=click.Path(dir_okay=False),
    metavar="",
    help="File to be used as a stream for DEBUG logging",
)
@click.option(
    "--config-file",
    default="",
    type=click.Path(dir_okay=False),
    metavar="",
    help="User configuration file (JSON format)",
)
@click.option("-v", "--verbose", is_flag=True, help="Will print more logging messages.")
def main(
    request: str,
    quality: str,
    output: str,
    only_tagging: bool,
    no_lyrics: bool,
    no_coverart: bool,
    no_tags: bool,
    save_lyrics: bool,
    backup: bool,
    log_level: str,
    debug_file: str,
    config_file: str,
    verbose: bool,
) -> None:
    """Pass URL of a song/album/playlist or trackingfile path."""

    # CLI options
    cli_config = {
        "quality": quality,
        "output": output,
        "only-tagging": only_tagging,
        "no-lyrics": no_lyrics,
        "no-coverart": no_coverart,
        "no-tags": no_tags,
        "save-lyrics": save_lyrics,
        "backup": backup,
        "log-level": log_level,
        "debug-file": debug_file,
        "config-file": config_file,
        "verbose": verbose,
    }

    # Merge default, user config, and CLI options
    Config.set_config(config_file, cli_config)

    configure_logger(Config.get_config("log-level"), Config.get_config("debug-file"))

    if config_file:
        logger.debug(f"Using config file: {config_file}")
    else:
        logger.debug("Using CLI options along with default configs")

    # Calling musicDL
    musicDL(request)


if __name__ == "__main__":
    main()
