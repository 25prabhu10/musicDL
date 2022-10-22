#!/usr/bin/env python
"""A command-line utility that downloads music from Saavn.

Downloads songs from albums and playlists. Embeds cover-art, meta-tags,
and lyrics. Pass on the URL of a song or an album or a playlist.

The downloaded music files will be saved in the user specified path
or in music folder of the user.

Usage is simple - call:

    `python -m musicDL <links, tracking files separated by space>`

Example:

    ``$ python -m musicDL https://www.jiosaavn.com/song/a8rghuievnsv``

A '.musicDLTrackingFile' is automatically created with the name of
the song/playlist/album. This file is cleaned up on successful download.

Failed files are cleaned up on download failure.
"""

__version__ = "0.5.1"
