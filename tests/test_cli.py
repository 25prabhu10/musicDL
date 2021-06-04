#!/usr/bin/env python
"""Collection of tests around musicDL's command-line interface."""

import pytest
from click.testing import CliRunner

from musicDL.__main__ import main


# Arrange
@pytest.fixture()
def cli_runner():
    """Fixture: That returns a helper function to run the musicDL cli."""
    runner = CliRunner()

    def cli_main(*cli_args, **cli_kwargs):
        """Run musicDL cli main with the given args."""
        return runner.invoke(main, cli_args, **cli_kwargs)

    return cli_main


@pytest.mark.parametrize("test_option,expected", [("-h", "Usage"), ("--help", "Usage")])
def test_cli_help(cli_runner, test_option, expected):
    """Test cli invocation displays help message with `help` flag."""
    # Act
    result = cli_runner(test_option)

    # Arrest
    assert result.exit_code == 0
    assert result.output.startswith(expected)


@pytest.mark.parametrize("test_option,expected", [("--version", "musicDL")])
def test_cli_version(cli_runner, test_option, expected):
    """Test correct version output by `musicDL` on cli invocation."""
    # Act
    result = cli_runner(test_option)

    # Arrest
    assert result.exit_code == 0
    assert result.output.startswith(expected)


# Arrange
@pytest.fixture(autouse=True)
def mock_functions(mocker):
    """Fixture: That mocks the main functions"""
    mocker.patch("musicDL.main.get_json_data_from_website", return_value={})
    mocker.patch("musicDL.main.extract_saavn_api_url", return_value="")
    mocker.patch("musicDL.main.get_json_data_from_api", return_value={})
    mocker.patch("musicDL.main.SongObj.from_raw_dict", return_value=({}, ""))
    mocker.patch(
        "musicDL.main.DownloadManager.resume_download_from_tracking_file",
        return_value="",
    )
    mocker.patch("musicDL.main.DownloadManager.download_songs", return_value="")


@pytest.mark.parametrize(
    "test_entity,expected",
    [
        ("https://www.jiosaavn.com/song/a", "Fetching Song...\n"),
        ("https://www.jiosaavn.com/s/playlist/a", "Fetching Playlist...\n"),
        ("temp.musicDLTrackingFile", "Preparing to resume download...\n"),
    ],
)
def test_cli_url(cli_runner, test_entity, expected):
    """Test if excepted entity is provided"""
    # Act
    result = cli_runner(test_entity)

    # Assert
    assert result.exit_code == 0
    assert result.output == expected


@pytest.mark.parametrize(
    "test_entity",
    [
        "memories",
        "https://www.spotify.com/a/album",
        "song",
        "https://www.youtube.com/s/song/",
    ],
)
def test_cli_url_exception(cli_runner, test_entity):
    """Test if given invalid entity program exist with code 3"""
    result = cli_runner(test_entity)

    assert result.exit_code == 3
    assert result.output == "Invalid entity passed\n"
