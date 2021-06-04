#!/usr/bin/env python
"""
Main entry point for the `musicDL` command.

Download music.
"""

import logging
import signal
import sys
from typing import Any  # For static type checking

from .config import Config
from .downloader import DownloadManager
from .handle_requests import get_json_data_from_api, get_json_data_from_website
from .services.saavn import extract_saavn_api_url, parse_request
from .SongObj import SongObj

logger = logging.getLogger(__name__)


def musicDL(request: str) -> None:
    """Download songs from Saavn.

    Args:
        request: URL of song/album/playlist or trackingfile path.
    """

    try:
        # The download manager takes output path as argument
        with DownloadManager() as downloader:

            def gracefulExit(signal: int, frame: Any) -> None:
                downloader.displayManager.close()
                sys.exit(0)

            signal.signal(signal.SIGINT, gracefulExit)
            signal.signal(signal.SIGTERM, gracefulExit)

            request_type = parse_request(request)
            logger.info(f"Type: {request_type}")

            if request_type == "trackingfile":
                print("Preparing to resume download...")
                downloader.resume_download_from_tracking_file(request)
            else:
                print(f"Fetching {request_type.capitalize()}...")

                # Ger JSON data from the Saavn web page
                raw_json_data = get_json_data_from_website(request)

                # Extract API URL from the extracted JSON data
                api_url = extract_saavn_api_url(request_type, raw_json_data)

                # Get the songs data from the API
                raw_songs_dict = get_json_data_from_api(api_url)

                # Get songObj list based on URL type and audio quality
                songs_obj_list = SongObj.from_raw_dict(raw_songs_dict, request_type)

                if Config.get_config("only-tagging"):
                    downloader.set_tags_for_songs(songs_obj_list)
                else:
                    downloader.download_songs(songs_obj_list)

        logger.info("Downloading Completed")
        sys.exit(0)
    except Exception as e:
        if not Config.get_config("verbose"):
            print(str(e))
        logger.exception(e)

        sys.exit(3)
