#!/usr/bin/env python
"""Collection of tests around saavn utility."""

import pytest
from musicDL.saavn import (
    identify_url,
    is_album_url,
    is_playlist_url,
    is_song_url,
    is_valid_saavn_url,
)
from musicDL.exceptions import InvalidSaavnURLException


@pytest.mark.parametrize(
    "test_url,expected",
    [
        ("https://www.jiosaavn.com/s/playlist/a", [("https://www.", "jio")]),
        ("https://www.saavn.com/s/song/a", [("https://www.", "")]),
        ("https://www.google.com/s/playlist/a", []),
        ("memory", []),
    ],
)
def test_is_valid_saavn_url(test_url, expected):
    """Test if given url is of saavn or not"""
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
    ],
)
def test_identify_url(test_url, expected):
    """Test if given url is of song/album/playlist"""
    assert identify_url(test_url) == expected


@pytest.fixture(
    params=[
        "h",
        "https://www.jiosaavn.com/aasd/album",
        "album",
        "https://www.jiosaavn.com/s/song/",
    ]
)
def invalid_test_url(request):
    """Fixture: That provides invalid test URLs"""
    return request.param


def test_identify_url_exceptions(invalid_test_url):
    """Test if given invalid url \
        InvalidSaavnURLException exception is raised or not"""
    with pytest.raises(InvalidSaavnURLException) as e:
        assert identify_url(invalid_test_url)

    # Check for exception message
    assert str(e.value) == "Invalid Saavn URL"
