#!/usr/bin/env python
import logging
import os
import sys
from datetime import date

import click

from musicDL import __version__
from musicDL.log import configure_logger
from musicDL.main import musicDL
import platform


logger = logging.getLogger(__name__)


def version_msg():
    """Return the musicDL version, location and Python powering it."""
    python_version = sys.version[:3]
    location = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    year = date.today().year
    message = "musicDL %(version)s from {} (Python {}) (c) {}"
    return message.format(location, python_version, year)


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.version_option(__version__, "-V", "--version", message=version_msg())
@click.argument("url", default=None, required=True, type=click.STRING)
@click.option(
    "-q",
    "--quality",
    # metavar="",
    default="high",
    type=click.Choice(["low", "medium", "high", "hd"], case_sensitive=False),
    help="""
    Audio Quality: low:96kbps, medium:128kbps, high:160kbps, or HD:320kbps
    """,
)
@click.option(
    "--log-level",
    default="debug",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    help="Set log verbosity",
)
@click.option(
    "--debug-file",
    default=None,
    type=click.Path(),
    help="File to be used as a stream for DEBUG logging",
)
@click.option(
    "--config-file",
    type=click.Path(),
    default=None,
    help="User configuration file (YAML format)",
)
def main(url, quality, log_level, debug_file, config_file):
    """
    Saavn download
    """
    configure_logger(log_level, debug_file)

    logger.debug(f"Python version: {sys.version}")
    logger.debug(f"Platform: {platform.platform()}")

    try:
        musicDL()
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
