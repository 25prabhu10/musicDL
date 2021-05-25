import asyncio
import concurrent
import logging
import sys
import traceback
from pathlib import Path
from typing import Any  # For static type checking

from .handle_requests import http_get
from .metadata import set_tags
from .progress_handlers import DisplayManager, DownloadTracker
from .services.lyrics import get_lyrics
from .SongObj import SongObj
from .utils import get_file_name

logger = logging.getLogger(__name__)


class DownloadManager:

    # Big pool sizes on slow connections will lead to more incomplete downloads
    poolSize = 4

    def __init__(self, output_dir: str):
        self.output_dir = output_dir

        # start a server for objects shared across processes
        self.displayManager = DisplayManager()
        self.downloadTracker = DownloadTracker()

        if sys.platform == "win32":
            # ! ProactorEventLoop is required on Windows to run subprocess asynchronously
            # ! it is default since Python 3.8 but has to be changed for previous versions
            loop = asyncio.ProactorEventLoop()
            asyncio.set_event_loop(loop)

        self.loop = asyncio.get_event_loop()
        # ! semaphore is required to limit concurrent asyncio executions
        self.semaphore = asyncio.Semaphore(self.poolSize)

        # ! thread pool executor is used to run blocking (CPU-bound) code from a thread
        self.thread_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.poolSize
        )

    def __enter__(self) -> Any:
        return self

    def __exit__(self, type, value, traceback):
        self.displayManager.close()

    def download_songs(self, song_obj_list: list[SongObj]) -> None:
        """
        `list<song_obj>` `song_obj_list` : list of songs to be downloaded

        RETURNS `~`

        downloads the given songs in parallel
        """

        logger.info("Downloading Initiated...")
        self.downloadTracker.clear()
        self.downloadTracker.load_song_list(song_obj_list)

        self.displayManager.set_song_count_to(len(song_obj_list))

        self._download_asynchronously(song_obj_list)

    def resume_download_from_tracking_file(self, tracking_file_path: str) -> None:
        """
        `str` `trackingFilePath` : path to a .spotdlTrackingFile

        RETURNS `~`

        downloads songs present on the .spotdlTrackingFile in parallel
        """

        self.downloadTracker.clear()
        self.downloadTracker.load_tracking_file(tracking_file_path)

        songObjList = self.downloadTracker.get_song_list()

        self.displayManager.set_song_count_to(len(songObjList))

        self._download_asynchronously(songObjList)

    async def download_song(self, song_obj: SongObj) -> None:
        """
        `songObj` `songObj` : song to be downloaded

        RETURNS `~`

        Downloads, Converts, Normalizes song & embeds metadata as ID3 tags.
        """

        # Since most errors are expected to happen within this function, we wrap in
        # expection catcher to prevent blocking on multiple downloads

        try:
            dispayProgressTracker = self.displayManager.new_progress_tracker(song_obj)

            media_name = song_obj.get_title()

            url = song_obj.get_media_url()

            file_name = get_file_name(url, media_name, song_obj.get_album_title())

            output_file_path = Path(self.output_dir, file_name)

            if output_file_path.is_file():
                if self.displayManager:
                    dispayProgressTracker.notify_download_skip()
                if self.downloadTracker:
                    self.downloadTracker.notify_download_completion(song_obj)

                # ! None is the default return value of all functions, we just explicitly define
                # ! it here as a continent way to avoid executing the rest of the function.
                return None

            with open(output_file_path, "wb") as output_file:
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

            # Raw media downloading complete
            if dispayProgressTracker:
                dispayProgressTracker.notify_saavn_download_completion()

            lyrics = get_lyrics(
                song_obj.get_song_id_saavn(), song_obj.has_saavn_lyrics()
            )

            if dispayProgressTracker:
                if lyrics:
                    song_obj.set_lyrics(lyrics)
                    dispayProgressTracker.notify_lyrics_download_completion()
                else:
                    dispayProgressTracker.notify_error(
                        "Couldn't find lyrics", "Searching Lyrics"
                    )

            is_tagging_successful = set_tags(str(output_file_path), song_obj)

            # Tagging completed
            if dispayProgressTracker:
                if is_tagging_successful:
                    dispayProgressTracker.notify_download_completion()
                else:
                    dispayProgressTracker.notify_error(
                        "Embeding tags failed", "Tagging"
                    )

            # Download complete
            if self.downloadTracker:
                self.downloadTracker.notify_download_completion(song_obj)

            logger.info(f"DOWNLOADED FILE IN: {str(output_file_path)}")

        except Exception as e:
            tb = traceback.format_exc()
            if dispayProgressTracker:
                dispayProgressTracker.notify_error(e, tb)
            else:
                raise e

    async def _pool_download(self, song_obj: SongObj) -> Any:
        # ! Run asynchronous task in a pool to make sure that all processes
        # ! don't run at once.

        # tasks that cannot acquire semaphore will wait here until it's free
        # only certain amount of tasks can acquire the semaphore at the same time
        async with self.semaphore:
            return await self.download_song(song_obj)

    def _download_asynchronously(self, song_obj_list: list[SongObj]) -> None:
        logger.info("Initiating Async Downloading ...")
        tasks = [self._pool_download(song) for song in song_obj_list]
        # call all task asynchronously, and wait until all are finished
        self.loop.run_until_complete(asyncio.gather(*tasks))
