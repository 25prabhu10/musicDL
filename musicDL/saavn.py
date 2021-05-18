#!/usr/bin/env python
"""
Contains all the Saavn utils

Verify URL
"""

import logging
import re

from musicDL.exceptions import InvalidSaavnURLException

logger = logging.getLogger(__name__)


def is_valid_saavn_url(url):
    """
    Check if the passed URL is a valid Saavn URL.
    URL should start with jiosaaavn.com
    """
    return re.findall(r"^(https://www.)?(jio)?saavn\.com.*?$", url)


def is_song_url(url):
    """
    Check if the passed URL is a song URL.
    """
    return re.findall(r"^(https://www.)?(jio)?saavn\.com/song/.*?$", url)


def is_album_url(url):
    """
    Check if the passed URL is an album URL.
    """
    return re.findall(r"^.*?(jio)?saavn.com/album/.*?", url)


def is_playlist_url(url):
    """
    Check if the passed URL is a JioSaavn playlist URL.
    """
    return re.findall(r"^.*?(jio)?saavn.com/(s/playlist|featured)/.*?", url)


def identify_url(url):
    """
    Identify the type of URL.

    User can provide URL for a song or album or playlist.
    """
    # Check if the url is a valid Saavn URL
    logger.debug(f"URL: {url}")

    if is_valid_saavn_url(url):
        if is_song_url(url):
            return "song"

        elif is_album_url(url):
            return "album"

        elif is_playlist_url(url):
            return "playlist"

    raise InvalidSaavnURLException("Invalid Saavn URL")
