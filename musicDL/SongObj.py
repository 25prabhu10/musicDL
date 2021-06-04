#!/usr/bin/env python
"""Song class"""

import logging
from html import unescape
from typing import Any, Type, TypeVar  # For static type checking

from slugify import slugify

from . import __version__
from .config import Config
from .handle_requests import http_get
from .utils import get_decrypted_url, get_language_code

logger = logging.getLogger(__name__)


# Create a generic variable that can be 'Parent', or any subclass.
T = TypeVar("T", bound="SongObj")


class SongObj:
    """Represents a Saavn song object."""

    # class variable for tracking file name
    __tracking_file_path = ""

    def __init__(
        self,
        json_dict: dict[str, Any],
        track_number: int,
        total_tracks: int,
        quality: str,
    ) -> None:
        """Initialize `SongObj` with song dict, track number, total tracks,
        and audio quality
        """
        self.__song_obj = json_dict
        self.__track_number = track_number
        self.__total_tracks = total_tracks
        self.__quality = quality
        self.__media_url = ""
        self._set_media_url()

    @classmethod
    def from_raw_dict(
        cls: Type[T],
        raw_json_dict: dict[str, Any],
        obj_type: str,
    ) -> list[T]:
        """Returns a list of SongObj instances.

         Args:
            raw_json_dict: Song details.
            obj_type: The type of URL.
            config: User configurations.

        Returns:
            song_obj_list: A list of SongObj instances.
        """

        tracking_file_path = "musicDL"

        # Extract tracking file name from song,  album title and plylist id
        if obj_type == "song":
            song_obj_list = list(raw_json_dict.values())
            tracking_file_path = song_obj_list[0]["song"]
        elif obj_type == "album":
            song_obj_list = raw_json_dict["songs"]
            tracking_file_path = raw_json_dict["title"]
        elif obj_type == "playlist":
            song_obj_list = raw_json_dict["songs"]
            tracking_file_path = raw_json_dict["listid"]

        cls.__tracking_file_path = slugify(text=tracking_file_path, max_length=150)

        total_tracks = len(song_obj_list)

        quality = Config.get_config("quality")

        song_obj_list = [
            cls(song_obj, index, total_tracks, quality)
            for index, song_obj in enumerate(song_obj_list, start=1)
        ]

        return song_obj_list

    @classmethod
    def get_tracking_file_path(cls: Type[T]) -> str:
        return cls.__tracking_file_path

    def __str__(self) -> str:
        if self.__song_obj:
            return str(self.__song_obj)
        return ""

    def _set_media_url(self) -> None:
        """Returns url of the media"""
        url = self.__song_obj.get("encrypted_media_url", "")
        quality = self.__quality
        is_320kbps = self.__song_obj.get("320kbps", False)
        self.__media_url = get_decrypted_url(url, quality, is_320kbps)

    def get_title(self) -> str:
        """Returns title of the song"""
        return unescape(self.__song_obj.get("song", ""))

    def get_album_title(self) -> str:
        """Returns name of album of the song"""
        return unescape(self.__song_obj.get("album", ""))

    def get_album_artists(self) -> str:
        """Returns name of album artists of the song"""
        return unescape(self.__song_obj.get("primary_artists", ""))

    def get_genre(self) -> str:
        """Returns genre of the song"""
        # TODO: Add genre
        return ""

    def get_track_number(self) -> str:
        """Returns a str for track number as (track_number/total_track)"""
        return f"{self.__track_number}/{self.__total_tracks}"

    def get_disc_number(self) -> str:
        """Returns a str for disk number as (side/disc_number)"""
        return "1/1"

    def get_composer(self) -> str:
        """Returns composer of the song"""
        return unescape(self.__song_obj.get("music", ""))

    def get_year(self) -> str:
        """Returns year of the song"""
        return str(self.__song_obj.get("year", ""))

    def get_release_date(self) -> str:
        """Returns date of release of the song"""
        return (
            self.__song_obj.get("release_date", "").replace("-", ",").replace("/", ",")
        )

    def get_copyright(self) -> str:
        """Returns copyright details of the song"""
        return unescape(self.__song_obj.get("copyright_text", ""))

    def get_encoded_by(self) -> str:
        """Returns the version of the program"""
        return f"musicDL v{__version__}"

    def get_duration(self) -> str:
        """Returns duration of the song in milliseconds"""
        milliseconds = int(self.__song_obj.get("duration", "0")) * 1000
        return str(milliseconds)

    def get_lang_code(self) -> str:
        """Returns language of the song"""
        language = self.__song_obj.get("language", "").capitalize()
        return get_language_code(language)

    def get_publisher(self) -> str:
        """Returns publisher of the song"""
        return unescape(self.__song_obj.get("label", ""))

    def get_song_id_saavn(self) -> str:
        """Returns saavn id of the song"""
        return self.__song_obj.get("id", "")

    def get_type(self) -> str:
        """Returns type of the media"""
        # TODO: Use it
        return self.__song_obj.get("type", "track")

    def has_saavn_lyrics(self) -> bool:
        """Returns if saavn lyrics is available"""
        return self.__song_obj.get("has_lyrics", "false") == "false"

    def set_lyrics(self, lyrics: str) -> None:
        """Sets lyrics of the song"""
        self.__song_obj["lyrics"] = lyrics

    def get_lyrics(self) -> str:
        """Returns lyrics of the song"""
        return self.__song_obj.get("lyrics", "")

    def get_sync_lyrics(self) -> str:
        """Returns sync-lyrics of the song"""
        # TODO: Get sync lyrics
        return ""

    def get_cover_image(self) -> str:
        """Returns url of cover image of the song"""
        url = self.__song_obj.get("image", "").replace("150x150", "500x500")
        return http_get(url)

    def get_media_url(self) -> str:
        """Returns url of the media"""
        return self.__media_url
