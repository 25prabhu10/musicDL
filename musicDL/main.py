#!/usr/bin/env python
"""
Main entry point for the `musicDL` command.

Download music.
"""

import logging
import sys
from typing import Any  # For static type checking

from .saavn import parse_url

logger = logging.getLogger(__name__)


def musicDL(url: str, config: dict[str, Any]) -> None:
    """Downloads songs from the URL using the given configurations.

    Args:
        url: A URL string of a song, an album, or a playlist.
        config: A dict containing configurations.
    """

    try:
        url_type = parse_url(url)

        print(f"Fetching {url_type.capitalize()}...")
        logger.debug(f"TYPE: {url_type}")

        sys.exit(0)
    except Exception as e:
        if not config["verbose"]:
            print(str(e))
        logger.exception(e)

        sys.exit(3)
