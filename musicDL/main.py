#!/usr/bin/env python
"""
Main entry point for the `musicDL` command.

Download music.
"""

import logging
import sys

from musicDL.saavn import identify_url

logger = logging.getLogger(__name__)


def musicDL(url, config):
    try:
        url_type = identify_url(url)
        logger.info(f"{url_type} URL passed")

        sys.exit(0)
    except Exception as e:
        if not config["verbose"]:
            print(str(e))
        logger.exception(e)

        sys.exit(3)
