#!/usr/bin/env python
"""
Handle all URL requests

Using requests module.
"""

import json
import logging
import re
from typing import Any, Optional, Union  # For static type checking

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


def _get_headers() -> dict[str, str]:
    """Returns fake headers.

    Returns:
        A dict containing fake headers
    """
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Charset": "UTF-8,*;q=0.5",
        "Accept-Encoding": "gzip,deflate,sdch",
        "Accept-Language": "en-US,en;q=0.8",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.74 Safari/537.36 Edg/79.0.309.43",  # noqa
    }

    return headers


def http_get(
    url: str, stream: bool = False
) -> Optional[Union[bytes, requests.Response]]:
    """Gets the content of a URL via sending a HTTP GET request.

    Args:
        url: A URL string.
        stream: A boolean value that allows streams.

    Returns:
        The response content as bytes.
        The response stream if stream is enabled.

    Raises:
        RequestException: An error occurred requesting the URL.
    """

    try:
        logger.debug(f"REQUESTING URL: {url}")
        res = requests.get(url, headers=_get_headers(), stream=stream, timeout=3)

        # Raise a requests.exceptions.HTTPError exception
        # If response status code is 4xx or 5xx.
        res.raise_for_status()

        if not stream:
            return res.content

        return res

    except RequestException as e:
        logger.exception(e)
        return None


def get_json_data_from_website(url: str) -> dict[str, Any]:
    """Extracts the json data from the Saavn Website.

    Args:
        url: A URL string of a song, an album, or a playlist.

    Returns:
        A dict that contains the extracted json data.

    Raises:
        ValueError: An error occurred fetching Saavn web page.
    """

    # Get the HTML page
    html_content = http_get(url)

    if html_content:
        logger.info("Extracting songs information...")
        soup = BeautifulSoup(html_content, features="html.parser")

        script_string = soup.find_all("script")[-1].string
        raw_object = (
            re.sub(re.compile(r"//.*?\n"), "", script_string)
            .replace("window.__INITIAL_DATA__ = ", "")
            .replace("\n", "")
            .replace("undefined", '""')
            .replace("null", '""')
        )
        raw_object = re.sub(re.compile(r"new Date\(.*?\)"), '""', raw_object)

        return json.loads(raw_object)

    raise ValueError("Failed to fetch the Saavn web page!!!")


def get_json_data_from_api(url: str) -> dict[str, Any]:
    """Gets the json data from URL via sending a HTTP GET request.

    Args:
        url: A URL string of a song, an album, or a playlist.

    Returns:
        A dict that contains the extracted json data.

    Raises:
        JSONDecodeError: An error occurred loading json data.
        ValueError: An error occurred getting songs information.
    """

    # Get the content from the URL
    content = http_get(url)

    if content:
        # Extract JSON data from the content
        raw_json_details = list(
            filter(lambda x: x.startswith("{"), content.decode("utf-8").splitlines())
        )

        # Load the JSON data as a dict
        if raw_json_details:
            return json.loads(raw_json_details[0])

    raise ValueError("Failed in getting songs information!!!")
