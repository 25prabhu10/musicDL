#!/usr/bin/env python
"""Contains all kinds of utility functions"""

import base64
import copy
import json
import logging
from typing import Any  # For static type checking

from .vendor.pyDes import ECB, PAD_PKCS5, des

logger = logging.getLogger(__name__)


def merge_dicts(original: dict[str, Any], overwrite: dict[str, Any]) -> dict[str, Any]:
    """Recursively update a dict with the key/value pair of another.

    Dict values that are dictionaries themselves will be updated, whilst
    preserving existing keys.

    Args:
        original (dict): The original dict.
        overwrite (dict): A dict that needs to be merged with the original dict.

    Returns:
        new_config (dict): A dict formed after the merger.
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
        url (str): Encrypted URL.

    Returns:
        dec_str (str): Decrypted URL.
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
        encrypt_url (str): Encrypted URL.
        quality (str): Audio quality.

    Returns:
        (str): Decrypted URL.
    """

    # Decrypt the media URL
    url = decrypt_url(encrypt_url)

    # Update the audio quality and type of media
    extension = "mp4"
    bit_rate = "_96"

    if quality == "medium":
        bit_rate = ""
        extension = "mp3"
        url = url.replace("https://aac", "http://h")
    elif quality == "high":
        bit_rate = "_160"
    elif quality == "hd":
        if is_320kbps:
            bit_rate = "_320"
        else:
            bit_rate = "_160"

    return url.replace("_96.mp4", f"{bit_rate}.{extension}")


def get_language_code(lang: str) -> str:
    """Returns ISO 639-2/B language code of the language.

    Args:
        lang (str): An ISO language name (English, Hindi).

    Returns:
        (str): ISO 639-2/B language code of the language.
            If the language was not found it will return "eng".
    """

    # Load the language codes
    lang_dict = json.load(open("lang_codes.json", "r", encoding="UTF-8"))
    if lang in lang_dict.keys():
        logger.debug(f"LANGUAGE: {lang}")
        return lang_dict[lang]
    return "eng"


def get_file_name(url: str, first_part: str, second_part: str) -> str:
    """Returns file name from given url, first and second part.

    Args:
        url (str): URL along with the file extension.
        first_part (str): First part of the file name.
        second_part (str): Second part of the file name.

    Returns:
        (str): The file name along with file extension.
    """

    # Create slugs of the given names
    if first_part.lower() != second_part.lower():
        file_name = f"{first_part} - {second_part}"
    else:
        file_name = first_part

    for disallowed_char in ["/", "\\", "*", "?", "<", ">", "|"]:
        if disallowed_char in file_name:
            file_name = file_name.replace(disallowed_char, "")

    # ! double quotes (") and semi-colons (:) are also disallowed characters but we would
    # ! like to retain their equivalents, so they aren't removed in the prior loop
    file_name = file_name.replace('"', "'").replace(":", "-")[:200]

    # Extract the file extension form the given URL
    extension = "m4a" if url.split(".")[-1] == "mp4" else "mp3"

    # Format file name
    return f"{file_name}.{extension}"
