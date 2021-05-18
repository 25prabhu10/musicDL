#!/usr/bin/env python
"""Main `musicDL` CLI."""
import logging
import os
import sys
from datetime import date

import click

from musicDL import __version__
from musicDL.config import get_config
from musicDL.log import configure_logger
from musicDL.main import musicDL

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
    show_default=True,
    type=click.Choice(["low", "medium", "high", "hd"], case_sensitive=False),
    metavar="",
    help="Audio Quality: low:96kbps, medium:128kbps, high:160kbps, or HD:320kbps",
)
@click.option(
    "--log-level",
    default="debug",
    show_default=True,
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    metavar="",
    help="Set log verbosity",
)
@click.option(
    "--debug-file",
    default=None,
    type=click.Path(),
    metavar="",
    help="File to be used as a stream for DEBUG logging",
)
@click.option(
    "--config-file",
    default=None,
    type=click.Path(),
    metavar="",
    help="User configuration file (YAML format)",
)
@click.option("--verbose", "-v", is_flag=True, help="Will print more logging messages.")
def main(url, quality, log_level, debug_file, config_file, verbose):
    """
    Saavn download
    """
    # CLI options
    cli_config = {
        "log-level": log_level,
        "debug-file": debug_file,
        "verbose": verbose,
        "musicDL": {
            "quality": quality,
        },
    }

    # Get default or user or CLI config
    config_dict = get_config(config_file, cli_config)

    configure_logger(
        config_dict["log-level"], config_dict["debug-file"], config_dict["verbose"]
    )

    # Calling musicDL
    musicDL(url, config_dict)


if __name__ == "__main__":
    main()
