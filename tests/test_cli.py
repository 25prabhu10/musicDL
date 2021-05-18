#!/usr/bin/env python
"""Collection of tests around musicDL's command-line interface."""

import pytest
from click.testing import CliRunner
from musicDL.__main__ import main


@pytest.fixture(scope="session")
def cli_runner():
    """Fixture that returns a helper function to run the musicDL cli."""
    runner = CliRunner()

    def cli_main(*cli_args, **cli_kwargs):
        """Run musicDL cli main with the given args."""
        return runner.invoke(main, cli_args, **cli_kwargs)

    return cli_main


@pytest.fixture(params=["-h", "--help"])
def help_cli_flag(request):
    """Pytest fixture return all help invocation options."""
    return request.param


def test_cli_help(cli_runner, help_cli_flag):
    """Test cli invocation display help message with `help` flag."""
    result = cli_runner(help_cli_flag)
    assert result.exit_code == 0
    assert result.output.startswith("Usage")


@pytest.fixture(params=["-V", "--version"])
def version_cli_flag(request):
    """Pytest fixture return both version invocation options."""
    return request.param


def test_cli_version(cli_runner, version_cli_flag):
    """Verify correct version output by `musicDL` on cli invocation."""
    result = cli_runner(version_cli_flag)
    assert result.exit_code == 0
    assert result.output.startswith("musicDL")


@pytest.mark.parametrize(
    "url,expected",
    [
        ("https://www.jiosaavn.com/s/playlist/a", ""),
        ("https://www.spotify.com/s/song/a", "Invalid Saavn URL\n"),
    ],
)
def test_cli_url(cli_runner, url, expected):
    """Verify if correct URL is provided"""

    result = cli_runner(url)

    assert result.exit_code == 0
    assert result.output == expected
