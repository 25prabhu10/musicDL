import asyncio
import concurrent
import sys
from pathlib import Path
from typing import Any  # For static type checking

from .SongObj import SongObj
from .utils import get_file_name
from .handle_requests import http_get


class DownloadManager:

    # Big pool sizes on slow connections will lead to more incomplete downloads
    poolSize = 4

    def __init__(self, output_dir: str):
        self.output_dir = output_dir

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

    def __exit__(self, type: Any, value: Any, traceback: Any) -> None:
        pass

    def download_songs(
        self, song_obj_list: list[SongObj], tracking_file_path: str
    ) -> None:
        """
        `list<song_obj>` `song_obj_list` : list of songs to be downloaded

        RETURNS `~`

        downloads the given songs in parallel
        """

        self._download_asynchronously(song_obj_list)

    async def download_song(self, song_obj: SongObj) -> None:
        """
        `songObj` `songObj` : song to be downloaded

        RETURNS `~`

        Downloads, Converts, Normalizes song & embeds metadata as ID3 tags.
        """

        # Since most errors are expected to happen within this function, we wrap in
        # expection catcher to prevent blocking on multiple downloads

        try:
            url = song_obj.get_media_url()

            file_name = get_file_name(
                url, song_obj.get_title(), song_obj.get_album_title()
            )

            output_file_path = Path(self.output_dir, file_name)

            with open(output_file_path, "wb") as output_file:
                response = http_get(url, stream=True)

                total = int(response.headers.get("content-length", 0))

                if total is None:
                    output_file.write(response.content)
                else:
                    for ch in response.iter_content(
                        chunk_size=max(int(total / 1000), 1024 * 1024)
                    ):
                        if ch:
                            output_file.write(ch)

        except Exception as e:
            print(e)
            pass

    async def _pool_download(self, song_obj: SongObj) -> Any:
        # ! Run asynchronous task in a pool to make sure that all processes
        # ! don't run at once.

        # tasks that cannot acquire semaphore will wait here until it's free
        # only certain amount of tasks can acquire the semaphore at the same time
        async with self.semaphore:
            return await self.download_song(song_obj)

    def _download_asynchronously(self, song_obj_list: list[SongObj]) -> None:
        tasks = [self._pool_download(song) for song in song_obj_list]
        # call all task asynchronously, and wait until all are finished
        self.loop.run_until_complete(asyncio.gather(*tasks))
