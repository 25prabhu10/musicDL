#!/usr/bin/env python
"""Main `musicDL` CLI."""

import logging
import os
import sys
from datetime import date

import click  # Creates beautiful command line interface

from . import __version__
from .config import get_config
from .log import configure_logger
from .main import musicDL

logger = logging.getLogger(__name__)


def version_msg() -> str:
    """Returns a `str` that contains musicDL version details.

    Returns:
        A `str` that contains musicDL version, module location,
        and Python version powering it.
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
@click.version_option(__version__, "-V", "--version", message=version_msg())
@click.argument("url", default=None, required=True, type=click.STRING)
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
    "--log-level",
    default="debug",
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
@click.option("--verbose", is_flag=True, help="Will print more logging messages.")
def main(
    url: str,
    quality: str,
    output: str,
    log_level: str,
    debug_file: str,
    config_file: str,
    verbose: bool,
) -> None:
    """Pass URL of a song/album/playlist"""

    # CLI options
    cli_config = {
        "log-level": log_level,
        "debug-file": debug_file,
        "verbose": verbose,
        "musicDL": {"quality": quality, "output": output},
    }

    # Merge default, user config, and CLI options
    config_dict = get_config(config_file, cli_config)

    configure_logger(
        config_dict["log-level"], config_dict["debug-file"], config_dict["verbose"]
    )

    # Calling musicDL
    musicDL(url, config_dict)


if __name__ == "__main__":
    main()
