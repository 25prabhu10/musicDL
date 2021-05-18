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
    """Fixture: Return all help invocation options."""
    return request.param


def test_cli_help(cli_runner, help_cli_flag):
    """Test cli invocation display help message with `help` flag."""
    result = cli_runner(help_cli_flag)
    assert result.exit_code == 0
    assert result.output.startswith("Usage")


@pytest.fixture(params=["-V", "--version"])
def version_cli_flag(request):
    """Fixture: Return both version invocation options."""
    return request.param


def test_cli_version(cli_runner, version_cli_flag):
    """Verify correct version output by `musicDL` on cli invocation."""
    result = cli_runner(version_cli_flag)
    assert result.exit_code == 0
    assert result.output.startswith("musicDL")


@pytest.fixture(
    params=[
        "https://www.jiosaavn.com/song/a" "https://www.jiosaavn.com/s/playlist/a",
    ],
)
def valid_test_url(request):
    """Fixture: That provides test URLs"""
    return request.param


def test_cli_url(cli_runner, valid_test_url):
    """Verify if correct URL is provided"""
    result = cli_runner(valid_test_url)

    assert result.exit_code == 0
    assert result.output == ""


# ("https://www.spotify.com/s/song/a", "Invalid Saavn URL\n"),


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
    """Test if given invalid url \
        InvalidSaavnURLException exception is raised or not"""
    result = cli_runner(invalid_test_url)

    assert result.exit_code == 3
    assert result.output == "Invalid Saavn URL\n"
