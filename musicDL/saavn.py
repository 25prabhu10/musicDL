#!/usr/bin/env python
"""
Contains all the Saavn related services

Validate the URL.
"""

import logging
import re

logger = logging.getLogger(__name__)


def is_valid_saavn_url(url: str) -> list[str]:
    """
    Check if the passed URL is a valid Saavn URL.
    URL should start with https://www.jiosaaavn.com
    """
    return re.findall(r"^(https://www.)?(jio)?saavn\.com.*?$", url)


def is_song_url(url: str) -> list[str]:
    """
    Check if the passed URL is of a song.
    """
    return re.findall(r"^(https://www.)?(jio)?saavn\.com/song/.*?$", url)


def is_album_url(url: str) -> list[str]:
    """
    Check if the passed URL is of an album.
    """
    return re.findall(r"^.*?(jio)?saavn.com/album/.*?", url)


def is_playlist_url(url: str) -> list[str]:
    """
    Check if the passed URL is of a playlist.
    """
    return re.findall(r"^.*?(jio)?saavn.com/(s/playlist|featured)/.*?", url)


def parse_url(url: str) -> str:
    """Identifies the type of URL.

    User can provide URL for a song or album or playlist.

    Args:
        url: A URL string of a song, an album, or a playlist.

    Returns:
        A string containing the type of URL:
            - song
            - album
            - playlist

    Raises:
      TypeError: An error occurred identifying the URL.
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

    raise TypeError("Invalid Saavn URL passed")
