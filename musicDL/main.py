#!/usr/bin/env python
"""
Main entry point for the `musicDL` command.

Download music.
"""

import logging
import signal
import sys
from typing import Any  # For static type checking

from .downloader import DownloadManager
from .handle_requests import get_json_data_from_api, get_json_data_from_website
from .services.saavn import extract_saavn_api_url, parse_url
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

        # Get songObj list based on URL type and audio quality
        audio_quality = config["musicDL"]["quality"]
        songs_obj_list = SongObj.from_raw_dict(raw_songs_dict, url_type, audio_quality)

        # The download manager takes output path as argument
        with DownloadManager(config["musicDL"]["output"]) as downloader:

            def gracefulExit(signal: int, frame: Any) -> None:
                downloader.displayManager.close()
                sys.exit(0)

            signal.signal(signal.SIGINT, gracefulExit)
            signal.signal(signal.SIGTERM, gracefulExit)

            downloader.download_songs(songs_obj_list)

        logger.info("Downloading Completed...")
        sys.exit(0)
    except Exception as e:
        if not config["verbose"]:
            print(str(e))
        logger.exception(e)

        sys.exit(3)
