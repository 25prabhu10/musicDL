#!/usr/bin/env python
"""
Main entry point for the `musicDL` command.

Download music.
"""

import logging

from musicDL.saavn import identify_url

logger = logging.getLogger(__name__)


def musicDL(url, config):
    identify_url(url)
