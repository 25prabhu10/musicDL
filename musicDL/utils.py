#!/usr/bin/env python
"""Contains all kinds of utility functions"""

import copy
from typing import Any  # For static type checking


def merge_dicts(original: dict[str, Any], overwrite: dict[str, Any]) -> dict[str, Any]:
    """Recursively updates a dict with the key/value pair of another.

    Dict values that are dictionaries themselves will be updated, whilst
    preserving existing keys.

    Args:
        original: The original dict.
        overwrite: A dict that needs to be merged with the original dict.

    Returns:
        A dict formed by merging the original dict with overwrite dict.
    """

    # Create a deep copy of original dict
    new_config = copy.deepcopy(original)

    for k, v in overwrite.items():
        # Make sure to preserve existing items in
        # nested dicts, for example `abbreviations`
        if isinstance(v, dict):
            new_config[k] = merge_dicts(original.get(k, {}), v)
        else:
            new_config[k] = v

    return new_config
