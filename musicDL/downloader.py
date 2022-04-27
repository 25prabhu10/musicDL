import asyncio
import concurrent
import logging
import sys
import traceback
from pathlib import Path
from typing import Any  # For static type checking

from .config import Config
from .handle_requests import http_get
from .metadata import set_tags
from .progress_handlers import DisplayManager, DownloadTracker
from .services import ffmpeg
from .services.lyrics import get_lyrics
from .SongObj import SongObj
from .utils import get_file_name

logger = logging.getLogger(__name__)


class DownloadManager:
    """Represents a Download Manager."""

    # Big pool sizes on slow connections will lead to more incomplete downloads
    poolSize: int = 4

    def __init__(self) -> None:
        """Initialize DownloadManger with DisplayManger, DownloadTracker,
        and asyncio operations. Along with the output directory.

        Args:
            output_dir: Path where the downloaded files need to be saved.
        """
        self.output_dir = Config.get_config("output")

        # start a server for objects shared across processes
        self.displayManager = DisplayManager()
        self.downloadTracker = DownloadTracker()

        if sys.platform == "win32":
            # ProactorEventLoop is required on Windows to run subprocess asynchronously
            # it is default since Python 3.8 but has to be changed for previous versions
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)

        self.loop = asyncio.get_event_loop()
        # semaphore is required to limit concurrent asyncio executions
        self.semaphore = asyncio.Semaphore(self.poolSize)

        # thread pool executor is used to run blocking (CPU-bound) code from a thread
        self.thread_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.poolSize
        )

        # ffmpeg path
        self.ffmpeg_path = Config.get_config("ffmpeg")

    def __enter__(self) -> Any:
        return self

    def __exit__(self, type, value, traceback):  # type: ignore
        self.displayManager.close()

    def _get_output_file_path(self, song_obj: SongObj) -> Path:
        """Retruns the media file path.

        Args:
            song_obj: Song details.

        Returns:
            The output file path
        """
        media_name = song_obj.get_title()

        url = song_obj.get_media_url()

        file_name = get_file_name(url, media_name, song_obj.get_album_title())

        return Path(self.output_dir, file_name)

    def download_lyrics(
        self,
        song_obj: SongObj,
        output_file_path: str,
        dispayProgressTracker: Any,
    ) -> None:
        """Download lyrics for the given song (:class:`musicDL.SongObj`).

        Args:
            song_obj: The song whose lyrics needs to be downloaded.
            output_file_path: Output path for the lyrics file.
            dispayProgressTracker: Progress tracker for the song.
        """

        lyrics = ""

        if not Config.get_config("no-lyrics"):
            lyrics = get_lyrics(
                song_id=song_obj.get_song_id_saavn(),
                has_saavn_lyrics=song_obj.has_saavn_lyrics(),
                title=song_obj.get_title(),
                artist=song_obj.get_album_artists(),
                file_path=output_file_path,
                save_lyrics=Config.get_config("save-lyrics"),
            )

        elif dispayProgressTracker:
            dispayProgressTracker.notify_lyrics_download_completion()
            return None

        if dispayProgressTracker:
            if lyrics:
                song_obj.set_lyrics(lyrics)
                dispayProgressTracker.notify_lyrics_download_completion()
            else:
                dispayProgressTracker.notify_error(
                    "Couldn't find lyrics", "Searching Lyrics"
                )

    def embed_tags(
        self, song_obj: SongObj, output_file_path: str, dispayProgressTracker: Any
    ) -> None:
        """Embed tags for the given song (:class:`musicDL.SongObj`).

        Args:
            song_obj: The song which needs to be embed with tags.
            output_file_path: Output path of the song.
            dispayProgressTracker: Progress tracker for the song.
        """

        is_tagging_successful = False

        if not Config.get_config("no-tags"):
            is_tagging_successful = set_tags(output_file_path, song_obj)

        elif dispayProgressTracker:
            dispayProgressTracker.notify_download_completion()
            return None

        # Tagging completed
        if dispayProgressTracker:
            if is_tagging_successful:
                dispayProgressTracker.notify_download_completion()
            else:
                dispayProgressTracker.notify_error("Embeding tags failed", "Tagging")

    def set_tags_for_songs(self, song_obj_list: list[SongObj]) -> None:
        """Set tags for the given list of songs (:class:`musicDL.SongObj`).

        Args:
            song_obj_list: List of songs to be tagged.
        """

        logger.info("Tagging Initiated")
        self.downloadTracker.clear()
        self.downloadTracker.load_song_list(song_obj_list)

        self.displayManager.set_song_count_to(len(song_obj_list))

        for song_obj in song_obj_list:
            try:
                dispayProgressTracker = self.displayManager.new_progress_tracker(
                    song_obj
                )

                output_file_path = self._get_output_file_path(song_obj)

                if not output_file_path.is_file():
                    if dispayProgressTracker:
                        dispayProgressTracker.notify_error("File not found", "Tagging")
                else:
                    if dispayProgressTracker:
                        dispayProgressTracker.notify_saavn_download_completion()

                    self.download_lyrics(
                        song_obj=song_obj,
                        output_file_path=str(output_file_path),
                        dispayProgressTracker=dispayProgressTracker,
                    )

                    self.embed_tags(
                        song_obj=song_obj,
                        output_file_path=str(output_file_path),
                        dispayProgressTracker=dispayProgressTracker,
                    )

                    logger.info(f"Successfully tagged {str(output_file_path)}")
            except Exception as e:
                tb = traceback.format_exc()
                if dispayProgressTracker:
                    dispayProgressTracker.notify_error(e, tb)
                else:
                    raise e

    def download_songs(self, song_obj_list: list[SongObj]) -> None:
        """Download the given list of songs (:class:`musicDL.SongObj`).

        Args:
            song_obj_list: List of songs to be downloaded.
        """

        logger.info("Downloading Initiated")
        self.downloadTracker.clear()
        self.downloadTracker.load_song_list(song_obj_list)

        self.displayManager.set_song_count_to(len(song_obj_list))

        self._download_asynchronously(song_obj_list)

    def resume_download_from_tracking_file(self, tracking_file_path: str) -> None:
        """Download songs from the trackingfile.

        Args:
            tracking_file_path: Path of the ``.musicDLTrackingFile``
        """

        self.downloadTracker.clear()
        self.downloadTracker.load_tracking_file(tracking_file_path)

        songObjList = self.downloadTracker.get_song_list()

        self.displayManager.set_song_count_to(len(songObjList))

        self._download_asynchronously(songObjList)

    async def download_song(self, song_obj: SongObj) -> None:
        """Download the given song (:class:`musicDL.SongObj`).

        Download, Convert, embed metadata, album art and lyrics.

        Args:
            song_obj: Song to be downloaded.
        """

        # Since most errors are expected to happen within this function, we wrap in
        # expection catcher to prevent blocking on multiple downloads
        try:
            dispayProgressTracker = self.displayManager.new_progress_tracker(song_obj)

            output_file_path = self._get_output_file_path(song_obj)

            if output_file_path.is_file():
                if self.displayManager:
                    dispayProgressTracker.notify_download_skip()
                if self.downloadTracker:
                    self.downloadTracker.notify_download_completion(song_obj)

                # None is the default return value of all functions, we just explicitly define
                # it here as a continent way to avoid executing the rest of the function.
                return None

            url = song_obj.get_media_url()

            with output_file_path.open("wb") as output_file:
                response = http_get(url, stream=True)

                total = int(response.headers.get("content-length", 0))

                if not total:
                    output_file.write(response.content)
                else:
                    for ch in response.iter_content(
                        chunk_size=max(int(total / 1000), 1024 * 1024)
                    ):
                        if ch:
                            output_file.write(ch)
                            if dispayProgressTracker:
                                dispayProgressTracker.update_progress_bar(total, ch)

            if not output_file_path.exists():
                if dispayProgressTracker:
                    dispayProgressTracker.notify_error("Download failed", "Downloading")
                return None

            # Raw media downloading complete
            if dispayProgressTracker:
                dispayProgressTracker.notify_saavn_download_completion()

            output_format = Config.get_config("output-format")
            if output_format:
                if not str(output_file_path).endswith(output_format):
                    output_file_path = await ffmpeg.convert(
                        output_format=output_format,
                        downloaded_file_path=str(output_file_path),
                        ffmpeg_path=self.ffmpeg_path,
                    )

            if dispayProgressTracker:
                dispayProgressTracker.notify_conversion_completion()

            self.download_lyrics(
                song_obj=song_obj,
                output_file_path=str(output_file_path),
                dispayProgressTracker=dispayProgressTracker,
            )

            self.embed_tags(
                song_obj=song_obj,
                output_file_path=str(output_file_path),
                dispayProgressTracker=dispayProgressTracker,
            )

            # Download complete
            if self.downloadTracker:
                self.downloadTracker.notify_download_completion(song_obj)

            logger.info(f"Downloaded file is {str(output_file_path)}")

        except Exception as e:
            tb = traceback.format_exc()
            if dispayProgressTracker:
                dispayProgressTracker.notify_error(e, tb)
            else:
                raise e

    async def _pool_download(self, song_obj: SongObj) -> Any:
        # Run asynchronous task in a pool to make sure that all processes
        # don't run at once.

        # tasks that cannot acquire semaphore will wait here until it's free
        # only certain amount of tasks can acquire the semaphore at the same time
        async with self.semaphore:
            return await self.download_song(song_obj)

    def _download_asynchronously(self, song_obj_list: list[SongObj]) -> None:
        logger.info("Initiating Async Downloading")
        logger.info(f"Downloading files into {self.output_dir}")
        tasks = [self._pool_download(song) for song in song_obj_list]
        # call all task asynchronously, and wait until all are finished
        self.loop.run_until_complete(asyncio.gather(*tasks))
