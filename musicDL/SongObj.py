#!/usr/bin/env python
"""Song class"""
import logging
from html import unescape
from typing import Any, Type, TypeVar  # For static type checking

from slugify import slugify

from musicDL.utils import get_decrypted_url, get_language_code

from . import __version__

logger = logging.getLogger(__name__)


# Create a generic variable that can be 'Parent', or any subclass.
T = TypeVar("T", bound="SongObj")


class SongObj:
    """Represents a Saavn song data.

    Attributes:
        json_dict: A boolean indicating if we like SPAM or not.
        eggs: An integer count of the eggs we have laid.
    """

    def __init__(
        self,
        json_dict: dict[str, Any],
        track_number: int,
        total_tracks: int,
        quality: str,
    ) -> None:
        """
        Inits SongObj with song dict, track number, total tracks,
        and audio quality
        """
        self.__song_obj = json_dict
        self.__track_number = track_number
        self.__total_tracks = total_tracks
        self.__quality = quality

    @classmethod
    def from_raw_dict(
        cls: Type[T],
        raw_json_dict: dict[str, Any],
        obj_type: str,
        config: dict[str, Any],
    ) -> tuple[list[T], str]:
        """Returns a list of SongObj instances and the tracking file name.

         Args:
            raw_json_dict: A dict containing song details.
            obj_type: A string containing the type of URL.
            config: A dict containing user configurations.

        Returns:
            A tuple of a list of SongObj instances and the tracking file name.
        """

        tracking_file_path = "musicDL"

        if obj_type == "song":
            song_obj_list = list(raw_json_dict.values())
            tracking_file_path = song_obj_list[0]["song"]
        elif obj_type == "album":
            song_obj_list = raw_json_dict["songs"]
            tracking_file_path = raw_json_dict["title"]
        elif obj_type == "playlist":
            song_obj_list = raw_json_dict["songs"]
            tracking_file_path = raw_json_dict["listid"]

        tracking_file_path = slugify(text=tracking_file_path, max_length=150)

        total_tracks = len(song_obj_list)

        song_obj_list = [
            cls(song_obj, index, total_tracks, config["quality"])
            for index, song_obj in enumerate(song_obj_list, start=1)
        ]

        return (song_obj_list, tracking_file_path)

    def get_title(self) -> str:
        """Returns title of the song"""
        return unescape(self.__song_obj.get("song", ""))

    def get_track_number(self) -> list[tuple[int, int]]:
        """Returns a list of a tuple of (track_number/total_track)"""
        return [(self.__track_number, self.__total_tracks)]

    def get_disc_number(self) -> list[tuple[int, int]]:
        """Returns a list of a tuple of (side/disc_number)"""
        return [(1, 1)]

    def get_genre(self) -> str:
        """Returns genre of the song"""
        return ""

    def get_album_artists(self) -> str:
        """Returns name of album artists of the song"""
        return unescape(self.__song_obj.get("primary_artists", ""))

    def get_album_title(self) -> str:
        """Returns name of album of the song"""
        return unescape(self.__song_obj.get("album", ""))

    def get_date(self) -> str:
        """Returns year of the song"""
        return str(self.__song_obj.get("year", ""))

    def get_release_year(self) -> str:
        """Returns year of release of the song"""
        try:
            if "release_date" in self.__song_obj:
                return self.__song_obj["release_date"].split("-")[0]
        except Exception as e:
            logger.exception(e)

        return self.get_date()

    def get_copyright(self) -> str:
        """Returns copyright details of the song"""
        return unescape(self.__song_obj.get("copyright_text", ""))

    def get_composer(self) -> str:
        """Returns composer of the song"""
        return unescape(self.__song_obj.get("music", ""))

    def get_encoded_by(self) -> str:
        """Returns the version of the program"""
        return f"musicDL v{__version__}"

    def get_song_id_saavn(self) -> str:
        """Returns saavn id of the song"""
        return self.__song_obj.get("id", "")

    def get_type(self) -> str:
        """Returns type of the media"""
        return self.__song_obj.get("type", "track")

    def get_lang_code(self) -> str:
        """Returns language of the song"""
        language = self.__song_obj.get("language", "").capitalize()
        return get_language_code(language)

    def get_duration(self) -> str:
        """Returns duration of the song"""
        return self.__song_obj.get("duration", 0)

    def get_starring(self) -> str:
        """Returns names of people starring in the song"""
        return unescape(self.__song_obj.get("starring", ""))

    def get_publisher(self) -> str:
        """Returns publisher of the song"""
        return unescape(self.__song_obj.get("label", ""))

    def get_lyrics(self) -> str:
        """Returns lyrics of the song"""
        return self.__song_obj.get("has_lyrics", False)

    def get_cover_image(self) -> str:
        """Returns url of cover image of the song"""
        return self.__song_obj.get("image", "").replace("150x150", "500x500")

    def get_media_url(self) -> str:
        """Returns url of the media"""
        url = self.__song_obj.get("encrypted_media_url", "")
        quality = self.__quality
        is_320kbps = self.__song_obj.get("320kbps", False)
        return get_decrypted_url(url, quality, is_320kbps)
