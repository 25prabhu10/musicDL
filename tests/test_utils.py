from musicDL import utils


def test_merge_configs():
    """Verify default and user config merged in expected way."""

    DEFAULT_CONFIG = {
        "log-level": "DEBUG",
        "debug-file": "",
        "config-file": "",
        "verbose": False,
        "musicDL": {
            "quality": "HD",
        },
    }

    user_config = {
        "debug-file": "",
        "config-file": "config.yml",
        "verbose": True,
        "musicDL": {
            "quality": "HD",
        },
    }

    expected_config = {
        "log-level": "DEBUG",
        "debug-file": "",
        "config-file": "config.yml",
        "verbose": True,
        "musicDL": {
            "quality": "HD",
        },
    }

    assert utils.merge_dicts(DEFAULT_CONFIG, user_config) == expected_config
