#!/usr/bin/env python
"""Collection of tests around Saavn utility."""

import pytest
from musicDL.services.saavn import (
    extract_saavn_api_url,
    is_album_url,
    is_playlist_url,
    is_song_url,
    is_valid_saavn_url,
    parse_request,
)


@pytest.mark.parametrize(
    "test_url,expected",
    [
        ("https://www.jiosaavn.com/s/playlist/a", [("https://www.", "jio")]),
        ("https://www.saavn.com/s/song/a", [("https://www.", "")]),
        ("https://www.google.com/s/playlist/a", []),
        ("memory", []),
        ("test.musicDLTrackingFile", []),
    ],
)
def test_is_valid_saavn_url(test_url, expected):
    """Test if given url is of Saavn or not"""
    assert is_valid_saavn_url(test_url) == expected


@pytest.mark.parametrize(
    "test_url,expected",
    [
        (
            "https://www.jiosaavn.com/song/skyrim-atmospheres/F1kNATt7QVE",
            [("https://www.", "jio")],
        ),
        ("https://www.saavn.com/song/a", [("https://www.", "")]),
        ("https://www.google.com/song/a", []),
        ("https://www.jiosaavn.com/s/playlist/a", []),
        ("song", []),
    ],
)
def test_is_song_url(test_url, expected):
    """Test if given url is of a song or not"""
    assert is_song_url(test_url) == expected


@pytest.mark.parametrize(
    "test_url,expected",
    [
        ("https://www.jiosaavn.com/album/a", ["jio"]),
        ("https://www.saavn.com/album/a", [""]),
        ("https://www.google.com/album/a", []),
        ("https://www.jiosaavn.com/s/playlist/a", []),
        ("album", []),
    ],
)
def test_is_album_url(test_url, expected):
    """Test if given url is of an album or not"""
    assert is_album_url(test_url) == expected


@pytest.mark.parametrize(
    "test_url,expected",
    [
        ("https://www.jiosaavn.com/s/playlist/a", [("jio", "s/playlist")]),
        ("https://www.saavn.com/s/playlist/a", [("", "s/playlist")]),
        ("https://www.google.com/s/playlist/a", []),
        ("https://www.jiosaavn.com/s/song/a", []),
        ("playlist", []),
    ],
)
def test_is_playlist_url(test_url, expected):
    """Test if given url is of a playlist or not"""
    assert is_playlist_url(test_url) == expected


@pytest.mark.parametrize(
    "test_url,expected",
    [
        (
            "https://www.jiosaavn.com/song/a",
            "song",
        ),
        ("https://www.jiosaavn.com/album/a", "album"),
        ("https://www.jiosaavn.com/s/playlist/a", "playlist"),
        ("test.musicDLTrackingFile", "trackingfile"),
    ],
)
def test_parse_request(test_url, expected):
    """Test if given url is of song/album/playlist"""
    assert parse_request(test_url) == expected


@pytest.mark.parametrize(
    "test_url",
    [
        "h",
        "https://www.jiosaavn.com/aasd/album",
        "album",
        "https://www.jiosaavn.com/s/song/",
    ],
)
def test_parse_url_exceptions(test_url):
    """Test if given invalid entity, TypeError exception is raised."""

    with pytest.raises(TypeError) as e:
        assert parse_request(test_url)

    assert e.typename == "TypeError"
    assert str(e.value) == "Invalid entity passed"


@pytest.fixture()
def valid_raw_json_data(request):
    """Fixture: That uses valid config path and CLI options"""
    return {
        "song": {"song": {"id": "Imagine"}},
        "albumView": {"album": {"id": "Album"}},
        "playlist": {"playlist": {"id": "new"}},
    }


@pytest.mark.parametrize(
    "request_type, expected",
    [
        (
            "song",
            (
                "https://www.jiosaavn.com/api.php?__call=song.getDetails&"
                "cc=in&_marker=0%3F_marker%3D0&_format=json&pids=Imagine"
            ),
        ),
        (
            "album",
            (
                "https://www.jiosaavn.com/api.php?_format=json"
                "&__call=content.getAlbumDetails&albumid=Album"
            ),
        ),
        (
            "playlist",
            (
                "https://www.jiosaavn.com/api.php?listid=new"
                "&_format=json&__call=playlist.getDetails"
            ),
        ),
    ],
)
def test_extract_saavn_api_url(valid_raw_json_data, request_type, expected):
    url = extract_saavn_api_url(request_type, valid_raw_json_data)

    assert url == expected


@pytest.mark.parametrize("request_type", ["test.musicDLTrackingFile", "", "songs"])
def test_extract_saavn_api_url_exception(valid_raw_json_data, request_type):
    with pytest.raises(ValueError) as e:
        assert extract_saavn_api_url(request_type, valid_raw_json_data)

    assert e.typename == "ValueError"
    assert str(e.value) == "Failed to extract API URL"
