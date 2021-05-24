#!/usr/bin/env python
"""
Main entry point for the `musicDL` command.

Download music.
"""

import logging
import sys
from typing import Any  # For static type checking

from .downloader import DownloadManager
from .handle_requests import get_json_data_from_api, get_json_data_from_website
from .saavn import extract_saavn_api_url, parse_url
from .SongObj import SongObj

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

        # Ger JSON data from the Saavn web page
        raw_json_data = get_json_data_from_website(url)

        # Extract API URL from the extracted JSON data
        api_url = extract_saavn_api_url(url_type, raw_json_data)

        # Get the songs data from the API
        raw_songs_dict = get_json_data_from_api(api_url)

        # Get songObj list and tracking file name
        [songs_obj_list, tracking_file_path] = SongObj.from_raw_dict(
            raw_songs_dict, url_type, config["musicDL"]
        )

        # The download manager takes output path as argument
        with DownloadManager(config["musicDL"]["output"]) as downloader:
            downloader.download_songs(songs_obj_list, tracking_file_path)

        sys.exit(0)
    except Exception as e:
        if not config["verbose"]:
            print(str(e))
        logger.exception(e)

        sys.exit(3)
