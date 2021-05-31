import json
import logging
import os
import re
from difflib import SequenceMatcher
from pathlib import Path

from lyricsgenius import Genius

from musicDL.handle_requests import http_get

logger = logging.getLogger(__name__)

# Set up Genius lyrics API
# Get Genius access token from environment variable GENIUS_ACCESS_TOKEN
token = os.environ["GENIUS_ACCESS_TOKEN"]
# Disable verbose mode for no prints from Genius
genius = Genius(token, verbose=False)


def get_lyrics(
    song_id: str,
    has_saavn_lyrics: bool,
    title: str,
    artist: str,
    save_lyrics: bool = False,
    file_path: str = ".",
) -> str:
    """Returns lyrics for the given song.

    Args:
        song_id (str): Saavn song id.
        has_saavn_lyrics (bool): True if Saavn has lyrics.
        title (str): Song title.
        artist (str): Artist names.
        save_lyrics (bool): Save lyrics into file if True.
        file_path (str): Path of the lyrics file.

    Returns:
        lyrics (str): Lyrics of the song.
    """

    lyrics = ""

    file_name = Path(file_path)
    file_name = file_name.with_suffix(".txt")

    # Try to fetch lyrics
    # Catch exceptions and return empty string.
    # Don't want to stop the downloading process if this fails.
    try:

        # If lyrics file exists then read from it.
        if file_name.exists():
            with file_name.open("r", encoding="UTF-8") as ly_file:
                return ly_file.read()

        # If Saavn lyrics exists get it from there.
        if has_saavn_lyrics:
            lyrics = get_lyrics_from_saavn(song_id)

        # Try to get it from Genius lyrics
        if not lyrics:
            lyrics = get_lyrics_from_genius(title, artist)

    except Exception as e:
        logger.error(f"LYRICS FAILED FOR: {title} - {artist}")
        logger.exception(e)

    if lyrics and save_lyrics:
        with file_name.open("w", encoding="UTF-8") as ly_file:
            ly_file.write(lyrics)

    return lyrics


def get_lyrics_from_saavn(song_id: str) -> str:
    """Returns lyrics based on the Saavn song id.

    Args:
        song_id (str): Saavn song id.

    Returns:
        lyrics (str): Lyrics of the song.
    """

    # Saavn lyrics
    logger.debug("Getting lyrics from saavn...")
    url = f"https://www.jiosaavn.com/api.php?__call=lyrics.getLyrics&lyrics_id={song_id}&ctx=web6dot0&api_version=4&_format=json&_marker=0"
    json_data = http_get(url).decode("utf-8")
    lyrics = json.loads(json_data).get("lyrics", "").replace("<br>", "\n")

    logger.debug(f"LYRICS FOR: {song_id}")
    return lyrics


def get_lyrics_from_genius(title: str, artist: str, retries: int = 0) -> str:
    """Fetches lyrics from Genius lyrics.

    Args:
        title (str): Song title.
        artist (str): Artist names.
        retries (int): Number of times to retry if song not found.

    Returns:
        (str): Lyrics of the song.
    """

    # Genius lyrics API
    logger.debug("Getting lyrics from genius...")

    # Keep a copy of title
    # This is to request Genius for lyrics with original title
    # If the modified title dose not work
    og_title = title

    if "(" in artist:
        artist = artist.split("(")[0].strip()

    if retries == 0 and "(" in title and "(Remix" not in title:
        title = title.split("(")[0].strip()

    song = genius.search_song(title=title, artist=artist)

    if song:
        title_ratio = SequenceMatcher(None, song.title, title).ratio()
        artist_ratio = SequenceMatcher(None, song.artist, artist).ratio()
        logger.debug(f"RATIOS OF: TITLE-{title_ratio}, ARTIST-{artist_ratio}")

        if title_ratio >= 0.68:
            logger.debug(f"LYRICS FOR: {title} - {artist}")
            return song.lyrics
        elif retries == 0:
            return get_lyrics_from_genius(og_title, artist, 1)

    elif "," in artist:
        artist = artist.split(",")[0].strip()
        return get_lyrics_from_genius(title, artist)

    logger.warning("Could not find lyrics from Genius")
    return ""


def get_sync_lyrics_from_file(file_path: str) -> list[tuple[str, int]]:
    """Returns synchronized lyrics from the file.

    Args:
        file_path (str): Path to lyrics file.

    Returns:
        sync_lyrics (list[tuple[str, int]]): Synchronized lyrics of the song.
    """

    sync_lyrics = []

    file_name = Path(file_path)
    sync_lyrics_path = file_name.with_suffix(".lrc")

    if sync_lyrics_path.exists():
        with open(sync_lyrics_path, "r", encoding="UTF-8") as sync_file:
            raw_sync_lyrics = [line.strip() for line in sync_file.readlines()]
        raw_sync_lyrics = [
            line for line in raw_sync_lyrics if re.match(r"\[(\d+):(\d+).(\d+)\]", line)
        ]
        sync_lyrics = [
            (line.split("]")[-1], get_milliseconds(line.split("]")[0].replace("[", "")))
            for line in raw_sync_lyrics
        ]

    return sync_lyrics


def get_milliseconds(timing: str) -> int:
    """Returns time in milliseconds.

    Args:
        timing (str): Time in minutes (00:00.00 format).

    Returns:
        (str): Time in milliseconds.
    """

    # Minutes
    parts = timing.split(":")
    minutes = int(parts[0])

    # Seconds and milliseconds
    parts = parts[1].split(".")
    seconds = int(parts[0])
    milliseconds = int(parts[1])

    return (minutes * 60 * 1000) + (seconds * 1000) + (milliseconds * 10)
