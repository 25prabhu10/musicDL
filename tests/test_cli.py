#!/usr/bin/env python
"""Collection of tests around musicDL's command-line interface."""

import pytest
from click.testing import CliRunner
from musicDL.__main__ import main


@pytest.fixture(scope="session")
def cli_runner():
    """Fixture: That returns a helper function to run the musicDL cli."""
    runner = CliRunner()

    def cli_main(*cli_args, **cli_kwargs):
        """Run musicDL cli main with the given args."""
        return runner.invoke(main, cli_args, **cli_kwargs)

    return cli_main


@pytest.fixture(params=["-h", "--help"])
def help_cli_flag(request):
    """Fixture: That returns all help invocation options."""
    return request.param


def test_cli_help(cli_runner, help_cli_flag):
    """Test cli invocation display help message with `help` flag."""
    result = cli_runner(help_cli_flag)
    assert result.exit_code == 0
    assert result.output.startswith("Usage")


@pytest.fixture(params=["-V", "--version"])
def version_cli_flag(request):
    """Fixture: That return both version invocation options."""
    return request.param


def test_cli_version(cli_runner, version_cli_flag):
    """Test correct version output by `musicDL` on cli invocation."""
    result = cli_runner(version_cli_flag)
    assert result.exit_code == 0
    assert result.output.startswith("musicDL")


@pytest.mark.parametrize(
    "test_url,expected",
    [
        ("https://www.jiosaavn.com/song/a", "Fetching Song...\n"),
        ("https://www.jiosaavn.com/s/playlist/a", "Fetching Playlist...\n"),
    ],
)
def test_cli_url(cli_runner, test_url, expected):
    """Test if correct URL is provided"""
    result = cli_runner(test_url)

    assert result.exit_code == 0
    assert result.output == expected


@pytest.fixture(
    params=[
        "memories",
        "https://www.spotify.com/a/album",
        "song",
        "https://www.youtube.com/s/song/",
    ]
)
def invalid_test_url(request):
    """Fixture: That provides invalid test URLs"""
    return request.param


def test_cli_url_exception(cli_runner, invalid_test_url):
    """Test if given invalid url program exist with code 3"""
    result = cli_runner(invalid_test_url)

    assert result.exit_code == 3
    assert result.output == "Invalid Saavn URL passed\n"
