#!/usr/bin/env python
"""
Convert lyrics from json to lrc.
"""

from pathlib import Path

import click
import json


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.argument("request", default=None, required=True, type=click.Path())
def main(request: str) -> None:
    _path = Path(request)

    if _path.is_dir():
        files = list(_path.glob("*.json"))
    else:
        files = [_path]

    extract(files)


def extract(files: list[Path]) -> None:
    for js_file in files:
        output_file = js_file.with_suffix(".lrc")
        with js_file.open("r") as fi:
            json_data = json.loads(fi.read())

        lyrics_data = json_data["lyrics"]

        with output_file.open("w") as fo:
            fo.write(f"[id: {lyrics_data['trackId']}]\n")
            fo.write(f"[by: {lyrics_data['provider']}]\n")
            fo.write(f"[lang: {lyrics_data['language']}]\n\n")

            for line in lyrics_data["lines"]:
                formatted_time = convert_to_milliseconds(line["time"])
                fo.write(f"[{formatted_time}]{line['words'][0]['string']}\n")


def convert_to_milliseconds(millis):
    minutes = int(millis / 60000)
    minutes = f"0{minutes}" if minutes < 10 else minutes
    seconds = int((millis % 60000) / 1000)
    seconds = f"0{seconds}" if seconds < 10 else seconds
    milliseconds = int(((millis % 60000) % 1000) / 10)
    milliseconds = f"0{milliseconds}" if milliseconds < 10 else milliseconds
    return f"{minutes}:{seconds}.{milliseconds}"


if __name__ == "__main__":
    main()
