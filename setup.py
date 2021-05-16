#!/usr/bin/env python
from setuptools import setup

from musicDL import __version__

with open("README.md", "r", encoding="utf-8") as readme_file:
    readme = readme_file.read()


setup(
    name="musicDL",
    version=__version__,
    description=(
        "A command-line utility that downloads "
        "song/albums/playlists from Saavn "
        "along with albumart, meta-tagsand and lyrics."
    ),
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Lois, Hal, Francis, Reese, Malcolm, Dewey and Jamie",
    author_email="",
    url="https://github.com/hutihobake2510/MusicDL",
    # Tests are included automatically:
    # https://docs.python.org/3.6/distutils/sourcedist.html#specifying-the-files-to-distribute
    packages=["musicDL"],
    python_requires=">=3.6",
    install_requires=[],
    license="MIT",
    zip_safe=False,
    keywords=[
        "spotify",
        "downloader",
        "download",
        "music",
        "youtube",
        "mp3",
        "m4a",
        "song",
        "album",
        "playlist",
        "metadata",
        "tags",
        "saavn",
        "lyrics",
    ],
    classifiers=[
        "Development Status :: 1 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: Conversion",
        "Topic :: Multimedia :: Video",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
    ],
    entry_points={"console_scripts": ["musicDL=musicDL.__main__:main"]},
)
