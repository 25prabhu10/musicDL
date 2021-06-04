#!/usr/bin/env python
"""
Contains all the Saavn related services

Validate the URL.
"""

import logging
import re
from typing import Any  # For static type checking

logger = logging.getLogger(__name__)


def is_valid_saavn_url(url: str) -> list[str]:
    """Check if the passed URL is a valid Saavn URL.
    URL should start with https://www.jiosaaavn.com
    """
    return re.findall(r"^(https://www.)?(jio)?saavn\.com.*?$", url)


def is_song_url(url: str) -> list[str]:
    """Check if the passed URL is of a song."""
    return re.findall(r"^(https://www.)?(jio)?saavn\.com/song/.*?$", url)


def is_album_url(url: str) -> list[str]:
    """Check if the passed URL is of an album."""
    return re.findall(r"^.*?(jio)?saavn.com/album/.*?", url)


def is_playlist_url(url: str) -> list[str]:
    """Check if the passed URL is of a playlist."""
    return re.findall(r"^.*?(jio)?saavn.com/(s/playlist|featured)/.*?", url)


def parse_request(request: str) -> str:
    """Identify the request type.

    User can provide URL for song/album/playlist or trackingfile path.

    Args:
        request: song/album/playlist URL or trackingfile path.

    Returns:
        The type of request:
            #. song
            #. album
            #. playlist
            #. trackingfile path

    Raises:
        TypeError: An error occurred identifying the request.
    """

    # Check if the url is a valid Saavn URL
    logger.debug(f"Request: {request}")

    if request.endswith(".musicDLTrackingFile"):
        return "trackingfile"

    elif is_valid_saavn_url(request):
        if is_song_url(request):
            return "song"

        elif is_album_url(request):
            return "album"

        elif is_playlist_url(request):
            return "playlist"

    raise TypeError("Invalid entity passed")


def extract_saavn_api_url(type_of_request: str, raw_json_data: dict[str, Any]) -> str:
    """Create and return Saavn API URL from json data.

    Args:
        type_of_data: Type of request passed by user
            #. song
            #. album
            #. playlist
        raw_json_data: Raw details of the song/album/playlist.

    Returns:
        The Saavn API URL.

    Raises:
        ValueError: An error occurred extracting API URL.
    """

    url = ""

    # Extract API URL based on the type of request
    if type_of_request == "song":
        _id = raw_json_data["song"]["song"]["id"]
        logger.debug(f"Song ID: {_id}")
        url = (
            "https://www.jiosaavn.com/api.php?__call=song.getDetails&"
            f"cc=in&_marker=0%3F_marker%3D0&_format=json&pids={_id}"
        )

    elif type_of_request == "album":
        _id = raw_json_data["albumView"]["album"]["id"]
        logger.debug(f"Album ID: {_id}")
        url = (
            "https://www.jiosaavn.com/api.php?_format=json"
            f"&__call=content.getAlbumDetails&albumid={_id}"
        )

    elif type_of_request == "playlist":
        _id = raw_json_data["playlist"]["playlist"]["id"]
        logger.debug(f"Playlist ID: {_id}")
        url = (
            f"https://www.jiosaavn.com/api.php?listid={_id}"
            "&_format=json&__call=playlist.getDetails"
        )

    if not url:
        raise ValueError("Failed to extract API URL")

    return url
