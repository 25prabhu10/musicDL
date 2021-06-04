#!/usr/bin/env python
"""
Set song metadata

Using EasyID3, ID3 and MP4 modules.
"""

import logging

from mutagen.easyid3 import EasyID3
from mutagen.easymp4 import EasyMP4
from mutagen.id3 import ID3
from mutagen.id3._frames import (
    APIC,
    COMM,
    PCNT,
    SYLT,
    TPOS,
    TPUB,
    TRCK,
    USER,
    USLT,
    WOAF,
)
from mutagen.mp4 import MP4, MP4Cover

from .services.lyrics import get_sync_lyrics_from_file
from .SongObj import SongObj

logger = logging.getLogger(__name__)


def set_tags(file_path: str, meta_tags: SongObj) -> bool:
    """Embed metadata into media files.

    Args:
        file_path: Path to the music file.
        meta_tags: Meta-tags of the song.
    """

    media_type = file_path.split(".")[-1]

    if media_type == "mp3":
        return set_id3_tags(file_path, meta_tags)
    elif media_type in ["aac", "m4a", "mp4"]:
        return set_mp4_tags(file_path, meta_tags)

    return False


def set_id3_tags(file_path: str, meta_tags: SongObj) -> bool:
    """Embed metadata into MP3 files.

    ID3v2.4 tag specification - see id3 docs:
    https://id3.org/id3v2.4.0-frames

    Args:
        music_file_path: Path to the music file.
        meta_tags: Meta-tags of the song.
    """

    # Embed song details
    logger.info("Tagging MP3 file")
    audiofile = EasyID3(file_path)
    # Get rid of all existing ID3 tags (if any exist)
    audiofile.delete()

    # Desc [MP3 tags]
    # Title [TIT2]
    audiofile["title"] = meta_tags.get_title()

    # Album name [TALB]
    audiofile["album"] = meta_tags.get_album_title()

    # Artists [TPE1]
    audiofile["artist"] = meta_tags.get_album_artists()
    # Album artist (all of 'em) [TPE2]
    audiofile["albumartist"] = meta_tags.get_album_artists()

    # Genres (pretty pointless if you ask me) [TCON]
    audiofile["genre"] = meta_tags.get_genre()
    # Composer [TCOM] - [\xa9wrt]
    audiofile["composer"] = meta_tags.get_composer()

    # Year [TDRC]
    audiofile["date"] = meta_tags.get_year()
    # Original release date [TDOR]
    audiofile["originaldate"] = meta_tags.get_release_date()

    # Copyright [TCOP]
    audiofile["copyright"] = meta_tags.get_copyright()
    # Name of the encoder [TENC]
    audiofile["encodedby"] = meta_tags.get_encoded_by()

    # Length of song [TLEN]
    audiofile["length"] = meta_tags.get_duration()
    # Audio language [TLAN]
    audiofile["language"] = meta_tags.get_lang_code()

    # Save as ID3 V2.4
    # As ID3 v2.3 isn't fully features
    # But windows doesn't support v2.4 until later versions of Win10
    audiofile.save(v2_version=4)

    # For supported id3 tags
    audiofile = ID3(file_path)

    # Track number [TRCK]
    audiofile["TRCK"] = TRCK(encoding=3, text=meta_tags.get_track_number())
    # Disc number [TPOS]
    audiofile["TPOS"] = TPOS(encoding=3, text=meta_tags.get_disc_number())
    # URL of the media file
    audiofile["WOAF"] = WOAF(url=meta_tags.get_media_url())
    # Play count
    audiofile["PCNT"] = PCNT(0)
    # Publisher
    audiofile["TPUB"] = TPUB(encoding=3, text=meta_tags.get_publisher())
    # Terms of use
    audiofile["USER"] = USER(encoding=3, text="For Private Use Only", lang="eng")
    # Comment [COMM]
    audiofile["COMM"] = COMM(
        encoding=3, text=f"Saavn ID: {meta_tags.get_song_id_saavn()}", lang="eng"
    )

    # Embed lyrics
    lyrics_txt = meta_tags.get_lyrics()
    if lyrics_txt:
        audiofile["USLT"] = USLT(
            encoding=3,
            desc="Lyrics",
            text=lyrics_txt,
            lang="eng",
        )

    # Embed sync-lyrics
    sync_lyrics = get_sync_lyrics_from_file(file_path)
    if sync_lyrics:
        audiofile["SYLT"] = SYLT(
            encoding=3,
            lang="eng",
            format=2,
            type=1,
            desc="Lyrics from MiniLyrics",
            text=sync_lyrics,
        )

    audiofile.save(v2_version=4)

    # Embed cover image
    album_art = meta_tags.get_cover_image()
    if album_art:
        audiofile["APIC"] = APIC(
            encoding=3,
            mime="image/jpeg",
            type=3,
            desc="Cover",
            data=album_art,
        )

    audiofile.save(v2_version=4)
    return True


def set_mp4_tags(file_path: str, meta_tags: SongObj) -> bool:
    """Embed metadata to M4A/AAC/MP4 files.

    MP4 specific tags - see mutagen docs:
    http://mutagen.readthedocs.io/en/latest/api/mp4.html

    Args:
        music_file_path: Path to the music file.
        meta_tags: Meta-tags of the song.
    """

    # Embed song details
    logger.info("Tagging M4A file")
    audiofile = EasyMP4(file_path)
    # Get rid of all existing ID3 tags (if any exist)
    audiofile.delete()

    # Desc [MP4 tags]
    # Title [\xa9nam]
    audiofile["title"] = meta_tags.get_title()

    # Album name [\xa9alb]
    audiofile["album"] = meta_tags.get_album_title()

    # Artists [\xa9ART]
    audiofile["artist"] = meta_tags.get_album_artists()
    # Album artist (all of 'em) [aART]
    audiofile["albumartist"] = meta_tags.get_album_artists()

    # Genres (pretty pointless if you ask me) [\xa9gen]
    audiofile["genre"] = meta_tags.get_genre()

    # Year [\xa9day]
    audiofile["date"] = meta_tags.get_year()

    # Copyright [cprt]
    audiofile["copyright"] = meta_tags.get_copyright()

    # Track number [trkn]
    audiofile["tracknumber"] = meta_tags.get_track_number()
    # Disc number [disk]
    audiofile["discnumber"] = meta_tags.get_disc_number()

    # Comment [\xa9cmt]
    audiofile["comment"] = f"Saavn ID: {meta_tags.get_song_id_saavn()}"

    # Ember basic meta-tags
    audiofile.save()

    audiofile = MP4(file_path)

    # Writer [\xa9wrt]
    audiofile["\xa9wrt"] = meta_tags.get_composer()
    # Name of the encoder []
    audiofile["\xa9too"] = meta_tags.get_encoded_by()

    # Embed lyrics
    lyrics_txt = meta_tags.get_lyrics()
    if lyrics_txt:
        audiofile["\xa9lyr"] = lyrics_txt

    # Embed cover image
    album_art = meta_tags.get_cover_image()
    if album_art:
        audiofile["covr"] = [MP4Cover(album_art, imageformat=MP4Cover.FORMAT_JPEG)]

    audiofile.save()
    return True
