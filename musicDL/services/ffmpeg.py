#!/usr/bin/env python
"""
Contains all the ffmpeg related services

Convert audio files from one format to another.
"""

import re
import subprocess
import sys
from pathlib import Path

from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
import asyncio


def has_correct_version(
    skip_version_check: bool = False, ffmpeg_path: str = "ffmpeg"
) -> bool:
    try:
        process = subprocess.Popen(
            [f"{ffmpeg_path}", "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
        )
    except FileNotFoundError:
        print("FFmpeg was not found, spotDL cannot continue.", file=sys.stderr)
        return False

    output = "".join(process.communicate())

    if skip_version_check is False:
        result = re.search(r"ffmpeg version \w?(\d+\.)?(\d+)", output)

        if result is None:
            print("Your FFmpeg version couldn't be detected", file=sys.stderr)
            return False

        version = result.group(0).replace("ffmpeg version ", "")

        # remove all non numeric characters from string example: n4.3
        version = re.sub(r"[a-zA-Z]", "", version)

        if float(version) < 4.3:
            print(
                f"Your FFmpeg installation is too old ({version}), please update to 4.3+\n",
                file=sys.stderr,
            )
            return False

    return True


async def convert(
    output_format: str, downloaded_file_path: str, ffmpeg_path: str
) -> Path:
    """Convert downloaded file to other formats.

    Using ffmpeg options such as:

    #. ``-v quiet``: Show nothing at all; be silent
    #. ``-i <INPUT>``: Input file path
    #. ``-acodec <CODEC>``: Audio codec being used
    #. ``-abr true``: automatically determines
    #. and passes the audio encoding bitrate to the filters and encoder
    #. ``


    Args:
        output_format: Output format such as MP3, AAC, or M4A.
        downloaded_file_path: Downloaded audio file path.
        ffmpeg_path: Path of `ffmpeg` application.
    """

    if ffmpeg_path is None:
        ffmpeg_path = "ffmpeg"

    downloaded_file_path = Path(downloaded_file_path)

    input_format = downloaded_file_path.suffix

    if input_format == ".mp3" and (output_format == "aac" or output_format == "m4a"):
        bitrate = MP3(str(downloaded_file_path)).info.bitrate
        codec = "aac"
    elif (input_format == ".aac" or input_format == ".m4a") and output_format == "mp3":
        bitrate = MP4(str(downloaded_file_path)).info.bitrate
        codec = "libmp3lame -abr true "
    else:
        return downloaded_file_path

    command = f'{ffmpeg_path} -v quiet -y -vn -i "%s" -c:a {codec} -b:a {bitrate}  "%s"'

    # bash/ffmpeg on Unix systems need to have escape char (\) for special characters: \$
    # alternatively the quotes could be reversed (single <-> double) in the command then
    # the windows special characters needs escaping (^): ^\  ^&  ^|  ^>  ^<  ^^
    output_file = downloaded_file_path.with_suffix(f".{output_format}")

    if sys.platform == "win32":
        formatted_command = command % (
            str(downloaded_file_path),
            str(output_file),
        )
    else:
        formatted_command = command % (
            str(downloaded_file_path).replace("$", r"\$"),
            str(output_file).replace("$", r"\$"),
        )

    process = await asyncio.subprocess.create_subprocess_shell(
        formatted_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    _, proc_err = await process.communicate()

    if process.returncode != 0:
        message = (
            f"ffmpeg returned an error ({process.returncode})"
            f'\nthe ffmpeg command was "{formatted_command}"'
            "\nffmpeg gave this output:"
            "\n=====\n"
            f"{proc_err.decode('utf-8')}"
            "\n=====\n"
        )

        print(message, file=sys.stderr)
        return downloaded_file_path

    downloaded_file_path.unlink()
    return output_file
