#!/usr/bin/env python
"""Collection of tests around loading musicDL config."""

import pytest
from musicDL import config


@pytest.fixture(params=["tests/test-config/valid-config.json"])
def valid_config_file_path(request):
    """Fixture: That returns path of a valid config file"""
    return request.param


test_expected_options = [
    {
        "log-level": "DEBUG",
        "debug-file": "",
        "config-file": "",
        "verbose": True,
        "musicDL": {"quality": "low", "output": "."},
    },
    {
        "log-level": "DEBUG",
        "debug-file": "",
        "config-file": "",
        "verbose": True,
        "musicDL": {"quality": "high", "output": "."},
    },
]

test_cli_options = [
    {},
    {
        "log-level": "DEBUG",
        "debug-file": "",
        "config-file": "",
        "musicDL": {
            "quality": "high",
        },
    },
]


@pytest.mark.parametrize(
    "cli_options,expected",
    [
        (test_cli_options[0], test_expected_options[0]),
        (test_cli_options[1], test_expected_options[1]),
    ],
)
def test_get_config(valid_config_file_path, cli_options, expected):
    """Test valid config opened and rendered correctly."""

    config_dict = config.get_config(valid_config_file_path, cli_options)

    assert config_dict == expected


# @pytest.mark.parametrize(
#     "config_path",
#     [
#         "tests/test-config/invalid-config.json",
#         "tests/test-config/empty-config.json",
#     ],
# )
# def test_get_config_does_not_exist(config_path):
#     """
#     Check that `json.JSONDecodeError` is raised when
#     attempting to get a invalid config file.
#     """

#     result = config.get_config(config_path, {})

#     assert result == "Invalid Saavn URL passed"
