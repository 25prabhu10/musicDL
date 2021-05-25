import json
import logging
from musicDL.handle_requests import http_get

logger = logging.getLogger(__name__)


def get_lyrics(song_id: str, has_saavn_lyrics: bool) -> str:
    if has_saavn_lyrics:
        return get_saavn_lyrics(song_id)


def get_saavn_lyrics(song_id: str) -> str:
    """Returns lyrics based on the Saavn song id.

    Returns:
        Returns lyrics based on the given Saavn song id.
    """

    # Saavn lyrics API
    logger.debug("Getting lyrics from saavn...")
    url = f"https://www.jiosaavn.com/api.php?__call=lyrics.getLyrics&lyrics_id={song_id}&ctx=web6dot0&api_version=4&_format=json&_marker=0"
    json_data = http_get(url).decode("utf-8")
    lyrics = json.loads(json_data).get("lyrics", "").replace("<br>", "\n")

    return lyrics
