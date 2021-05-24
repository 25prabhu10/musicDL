#!/usr/bin/env python
"""Contains all kinds of utility functions"""

import base64
import copy
from typing import Any  # For static type checking

from .vendor.pyDes import ECB, PAD_PKCS5, des


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


def decrypt_url(url: str) -> str:
    """Returns decrypted URL.

    Uses external module called pyDes to decrypt the URL.

    Args:
        url: A string containing encrypted URL

    Returns:
        A string containing decrypted URL.
    """

    # Key and IV are coded in plaintext in the app when de-compiled
    # and its pretty insecure to decrypt urls to the mp3 at the client side
    # these operations should be performed at the server side.
    des_cipher = des(b"38346591", ECB, b"\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)
    enc_url = base64.b64decode(url.strip())
    dec_url = des_cipher.decrypt(enc_url, padmode=PAD_PKCS5).decode("utf-8")

    return dec_url


def get_decrypted_url(encrypt_url: str, quality: str, is_320kbps: bool) -> str:
    """Returns decrypted URL based on the audio quality.

    Args:
        url: A string containing encrypted URL

    Returns:
        A string containing decrypted URL.
    """

    # Decrypt the media URL
    url = decrypt_url(encrypt_url)

    # Update the audio quality and type of media
    extension = "mp4"
    bit_rate = 96

    if quality == "medium":
        bit_rate = 120
        extension = "mp3"
        url = url.replace("https://aac", "http://h")
    elif quality == "high":
        bit_rate = 160
    elif quality == "hd":
        if is_320kbps:
            bit_rate = 320
        else:
            bit_rate = 160

    return url.replace("96.mp4", f"{bit_rate}.{extension}")
