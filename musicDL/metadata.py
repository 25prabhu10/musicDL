#!/usr/bin/env python
"""
Set song metadata

Using EasyID3, ID3 and MP4 modules.
"""

from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3
from mutagen.id3._frames import APIC, SYLT, TORY, TPUB, TYER, USER, USLT, WCOP
from mutagen.mp4 import MP4, MP4Cover

from .constants import M4A_TAG_PRESET, MP3_TAG_PRESET
from .SongObj import SongObj


def set_tags(file_path: str, meta_tags: SongObj) -> bool:
    """Embed metadata to media files.

    Args:
        file_path: Path to the music file.
        meta_tags: A dict containing meta-tags of the song.
    """

    media_type = file_path.split(".")[-1]

    if media_type == "mp3":
        return set_id3_tags(file_path, meta_tags)
    elif media_type == "aac":
        return set_mp4_tags(file_path, meta_tags)
    else:
        return False

    return True


def set_id3_tags(file_path: str, meta_tags: SongObj) -> bool:
    """Embed metadata to MP3 files.

    Args:
        music_file_path: Path to the music file.
        meta_tags: A dict containing meta-tags of the song.
    """

    # Embed song details
    # we save tags as both ID3 v2.3 and v2.4
    # The simple ID3 tags
    audiofile = EasyID3(file_path)
    # Get rid of all existing ID3 tags (if any exist)
    audiofile.delete()
    # Ember basic meta-tags
    _embed_basic_metatags(audiofile, meta_tags, MP3_TAG_PRESET)

    # Type of media
    audiofile["media"] = meta_tags.get_type()
    audiofile["length"] = meta_tags.get_duration()
    audiofile["language"] = meta_tags.get_lang_code()
    audiofile["website"] = meta_tags.get_media_url()

    # save as both ID3 v2.3 & v2.4 as v2.3 isn't fully features and
    # windows doesn't support v2.4 until later versions of Win10
    audiofile.save(v2_version=3)

    # For supported id3 tags
    audiofile = ID3(file_path)
    audiofile["TORY"] = TORY(encoding=3, text=meta_tags.get_date())
    audiofile["TYER"] = TYER(encoding=3, text=meta_tags.get_date())
    audiofile["TPUB"] = TPUB(encoding=3, text=meta_tags.get_publisher())
    audiofile["USER"] = USER(
        encoding=3, desc="Terms of use", text="For Private Use Only", lang="eng"
    )
    audiofile["WCOP"] = WCOP(url=meta_tags.get_media_url())

    # Embed lyrics
    audiofile["USLT::'eng'"] = USLT(
        encoding=3,
        desc="Lyrics",
        text=meta_tags.get_lyrics(),
        lang="eng",
    )

    # Embed sync-lyrics
    audiofile["SYLT"] = SYLT(
        encoding=3,
        lang="eng",
        format=2,
        type=1,
        desc="Lyrics were Saved by MiniLyrics.",
        text=meta_tags.get_sync_lyrics(),
    )

    audiofile.save(v2_version=3)

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

    audiofile.save(v2_version=3)
    return True


def set_mp4_tags(file_path: str, meta_tags: SongObj) -> bool:
    """Embed metadata to M4A/AAC/MP4 files.

    Args:
        music_file_path: Path to the music file.
        meta_tags: A dict containing meta-tags of the song.
    """

    # Embed song details
    audiofile = MP4(file_path)
    # Get rid of all existing ID3 tags (if any exist)
    audiofile.delete()
    # Ember basic meta-tags
    _embed_basic_metatags(audiofile, meta_tags, M4A_TAG_PRESET)

    # Embed lyrics
    audiofile["lyrics"] = meta_tags.get_lyrics()

    # Embed cover image
    album_art = meta_tags.get_cover_image()
    if album_art:
        audiofile["covr"] = [MP4Cover(album_art, imageformat=MP4Cover.FORMAT_JPEG)]

    audiofile.save()
    return True


def _embed_basic_metatags(audiofile, meta_tags, preset_tags):
    """Embed metadata common to both MP3 and M4A/AAC/MP4 files.

    Args:
        audiofile: Path to the music file.
        meta_tags: A dict containing meta-tags of the song.
        preset_tags: A dict containing MP3 or M4A/AAC/MP4 tag names.
    """

    # Song name
    audiofile[preset_tags["title"]] = meta_tags.get_title()
    audiofile[preset_tags["titlesort"]] = meta_tags.get_title()
    # Track number
    audiofile[preset_tags["tracknumber"]] = meta_tags.get_track_number()
    # Disc number
    audiofile[preset_tags["discnumber"]] = meta_tags.get_disc_number()
    # Genres (pretty pointless if you ask me)
    # We only apply the first available genre as ID3 v2.3 doesn't support multiple
    # Genres and ~80% of the world PC's run Windows - an OS with no ID3 v2.4 support
    audiofile[preset_tags["genre"]] = meta_tags.get_genre()
    # All involved artists
    audiofile[preset_tags["artist"]] = meta_tags.get_album_artists()
    # Album name
    audiofile[preset_tags["album"]] = meta_tags.get_album_title()
    # Album artist (all of 'em)
    audiofile[preset_tags["albumartist"]] = meta_tags.get_album_artists()
    # Album release date (to what ever precision available)
    audiofile[preset_tags["date"]] = meta_tags.get_date()
    audiofile[preset_tags["originaldate"]] = meta_tags.get_release_year()
    audiofile[preset_tags["copyright"]] = meta_tags.get_copyright()
    # Composer or writer
    audiofile[preset_tags["writer"]] = meta_tags.get_composer()
    audiofile[preset_tags["encoded"]] = meta_tags.get_encoded_by()
