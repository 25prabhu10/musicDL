import ast
import logging
import shutil
import time
from pathlib import Path
from typing import Any, Optional, TypeVar  # For static type checking

from rich.console import Console, JustifyMethod, OverflowMethod, detect_legacy_windows
from rich.highlighter import Highlighter
from rich.progress import BarColumn, Progress, ProgressColumn, Task, TimeRemainingColumn
from rich.style import StyleType
from rich.text import Text
from rich.theme import Theme

from .config import Config
from .constants import progress_bar_theme
from .SongObj import SongObj

logger = logging.getLogger(__name__)

# Create a generic variable that can be 'Parent', or any subclass.
T = TypeVar("T", bound="SongObj")

custom_theme = Theme(progress_bar_theme)


class SizedTextColumn(ProgressColumn):  # type: ignore
    """A column containing text."""

    def __init__(
        self,
        text_format: str,
        style: StyleType = "none",
        justify: JustifyMethod = "left",
        markup: bool = True,
        highlighter: Highlighter = None,
        overflow: Optional[OverflowMethod] = None,
        width: int = 20,
    ) -> None:
        self.text_format = text_format
        self.justify = justify
        self.style = style
        self.markup = markup
        self.highlighter = highlighter
        self.overflow = overflow
        self.width = width
        super().__init__()

    def render(self, task: Task) -> Text:
        _text = self.text_format.format(task=task)
        if self.markup:
            text = Text.from_markup(_text, style=self.style, justify=self.justify)
        else:
            text = Text(_text, style=self.style, justify=self.justify)
        if self.highlighter:
            self.highlighter.highlight(text)

        text.truncate(max_width=self.width, overflow=self.overflow, pad=True)
        return text


class DisplayManager:
    def __init__(self) -> None:

        # Change color system if "legacy" windows terminal
        # to prevent wrong colours displaying
        self.isLegacy = detect_legacy_windows()

        # dumb_terminals automatically handled by rich.
        # Color system is too but it is incorrect
        # for legacy windows ... so no color for y'all.
        self.console = Console(
            theme=custom_theme, color_system="truecolor" if not self.isLegacy else None
        )

        self._richProgressBar = Progress(
            SizedTextColumn(
                "[white]{task.description}",
                overflow="ellipsis",
                width=int(self.console.width / 3),
            ),
            SizedTextColumn("{task.fields[message]}", width=18, style="nonimportant"),
            BarColumn(bar_width=None, finished_style="green"),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeRemainingColumn(),
            console=self.console,
            # Normally when you exit the progress context manager (or call stop())
            # the last refreshed display remains in the terminal with the cursor on
            # the following line. You can also make the progress display disappear on
            # exit by setting transient=True on the Progress constructor
            transient=self.isLegacy,
        )

        self.songCount = 0
        self.overallTaskID = None
        self.overallProgress = 0
        self.overallTotal = 100
        self.overallCompletedTasks = 0
        self.quiet = False

        # Basically a wrapper for rich's: with ... as ...
        self._richProgressBar.__enter__()

    def print(self, *text: Any, color: str = "green") -> None:
        """Use this self.print to replace default print().

        Args:
            text: Text to be printed to screen
        """

        if self.quiet:
            return

        line = ""
        for item in text:
            line += str(item) + " "

        if color:
            self._richProgressBar.console.print(f"[{color}]{line}")
        else:
            self._richProgressBar.console.print(line)

    def set_song_count_to(self, song_count: int) -> None:
        """Set the size of the progressbar based on the number of songs.

        Args:
            song_count: The number of songs being downloaded.
        """

        # All calculations are based of the arbitrary choice that 1 song consists of
        # 100 steps/points/iterations
        logger.info(f"COUNT: {song_count}")
        self.songCount = song_count

        self.overallTotal = 100 * song_count

        if self.songCount > 4:
            self.overallTaskID = self._richProgressBar.add_task(
                description="Total",
                processID="0",
                message=f"{self.overallCompletedTasks}/{int(self.overallTotal / 100)} complete",
                total=self.overallTotal,
                visible=(not self.quiet),
            )

    def update_overall(self) -> None:
        """Update the overall progress bar."""

        # If the overall progress bar exists
        if self.overallTaskID is not None:
            self._richProgressBar.update(
                self.overallTaskID,
                message=f"{self.overallCompletedTasks}/{int(self.overallTotal / 100)} complete",
                completed=self.overallProgress,
            )

    def new_progress_tracker(self, song_obj: SongObj) -> Any:
        """Returns new instance of `_ProgressTracker`
        that follows the `song_obj` download subprocess.
        """

        return _ProgressTracker(self, song_obj)

    def close(self) -> None:
        """Clean up rich"""

        self._richProgressBar.stop()


class _ProgressTracker:
    def __init__(self, parent: Any, song_obj: SongObj) -> None:
        self.parent = parent
        self.song_obj = song_obj

        self.progress = 0.0
        self.oldProgress = 0.0
        self.downloadID = 0
        self.status = ""

        self.taskID = self.parent._richProgressBar.add_task(
            description=song_obj.get_title(),
            processID=str(self.downloadID),
            message="Download Started",
            total=100,
            completed=self.progress,
            start=False,
            visible=(not self.parent.quiet),
        )

    def notify_download_skip(self) -> None:
        """Update progress bar to reflect a song being skipped"""

        self.progress = 100
        self.update("Skipping")

    def update_progress_bar(self, file_size: float, chunk: bytes) -> None:
        """Update progress bar to reflect media being downloaded.

        Args:
            file_size: A string containing total file size.
            chunk: The bytes that were downloaded.
        """

        # This will be called until download is complete, i.e we get an overall
        # How much of the file was downloaded this iteration scaled put of 90.
        # It's scaled to 90 because, the arbitrary division of each songs 100
        # iterations is (a) 90 for download (b) 5 for getting lyrics
        # and (c) 5 for tag embedding
        iterFraction = len(chunk) / file_size * 90

        self.progress = self.progress + iterFraction
        self.update("Downloading")

    def notify_saavn_download_completion(self) -> None:
        """Update progressbar to reflect a audio download being completed"""

        self.progress = 90  # self.progress + 5
        self.update("Converting")

    def notify_conversion_completion(self) -> None:
        """Update progressbar to reflect a audio conversion being completed"""

        self.progress = 95  # self.progress + 5
        self.update("Searching lyrics")

    def notify_lyrics_download_completion(self) -> None:
        """Update progressbar to reflect getting lyrics being completed"""

        self.progress = 99  # self.progress + 5
        self.update("Tagging")

    def notify_download_completion(self) -> None:
        """Update progressbar to reflect a download being completed"""

        # Download completion implies ID# tag embedding was just finished
        self.progress = 100  # self.progress + 5
        self.update("Done")

    def notify_error(self, e: Any, tb: str) -> None:
        """Show error message in progress bar.

        Freezes the progress bar and prints the traceback received.

        Args:
            e: error message
            tb: traceback
        """

        self.update(message="Error " + self.status)

        message = (
            f"Error: {e}\tWhile {self.status}: {self.song_obj.get_title()}\n {str(tb)}"
        )
        self.parent.print(message, color="red")

    def update(self, message: str = "") -> None:
        """Update the progress bar along with message, called at every event."""

        self.status = message

        # The change in progress since last update
        delta = self.progress - self.oldProgress

        # Update the progress bar
        # `start_task` called every time to ensure progress
        # is remove from indeterminate state
        self.parent._richProgressBar.start_task(self.taskID)
        self.parent._richProgressBar.update(
            self.taskID,
            description=self.song_obj.get_title(),
            processID=str(self.downloadID),
            message=message,
            completed=self.progress,
        )

        # If task is complete
        if self.progress == 100 or message == "Error":
            self.parent.overallCompletedTasks += 1
            if self.parent.isLegacy:
                self.parent._richProgressBar.remove_task(self.taskID)

        # Update the overall progress bar
        self.parent.overallProgress += delta
        self.parent.update_overall()

        self.oldProgress = self.progress


class DownloadTracker:
    def __init__(self) -> None:
        self.song_obj_list: list[SongObj] = []
        self.saveFile: Optional[Path] = None

    def load_tracking_file(self, tracking_file_path: str) -> None:
        """Read SongObj's from trackingfile.

        Args:
            tracking_file_path: Path to the .musicDLTrackingFile
        """

        # Attempt to read .musicDLTrackingFile, raise exception if file can't be read
        tracking_file = Path(tracking_file_path)
        if not tracking_file.is_file():
            raise FileNotFoundError(
                f"No such tracking file found: {tracking_file_path}"
            )

        with tracking_file.open("rb") as file_handle:
            self.song_obj_list = ast.literal_eval(file_handle.read().decode())

        # Save path to .musicDLTrackingFile
        self.saveFile = tracking_file

    def load_song_list(self, song_obj_list: list[SongObj]) -> None:
        """Prepare to track download of provided SongObj's.

        Args:
            song_obj_list: List of SongObj's to be downloaded.
        """

        self.song_obj_list = song_obj_list

        # Create a backup .musicDLTrackingFile file
        self.backup_to_disk()

        if Config.get_config("backup"):
            backup_file = Path(
                Config.get_config("output"), f"{int(time.time())} - {self.saveFile}"
            )  # type: ignore
            shutil.copy(self.saveFile, backup_file)  # type: ignore

    def get_song_list(self) -> list[SongObj]:
        """Returns list of SongObj's representing songs yet to be downloaded.

        Returns:
            song_obj_list: List of `SongObj`'s yet to be downloaded.
        """

        return self.song_obj_list

    def backup_to_disk(self) -> None:
        """Backup SongObjs that are yet to be downloaded to a .musicDLTrackingFile"""

        # remove tracking file if no songs left in queue
        # we use 'return None' as a convenient exit point
        if len(self.song_obj_list) == 0:
            if self.saveFile and self.saveFile.is_file():
                self.saveFile.unlink()
            return None

        # prepare data-dumps pf all SongObj's yet to be downloaded
        song_data_dump: list[str] = []

        for song in self.song_obj_list:
            song_data_dump.append(str(song))

        # the default naming of a tracking file is
        # $nameOfSong/album/playlistID.musicDLTrackingFile,
        if not self.saveFile:
            self.saveFile = Path(
                SongObj.get_tracking_file_path() + ".musicDLTrackingFile"
            )
            logger.info(f"BACKUP FILE: {self.saveFile}")

        # backup to file
        # we use 'wb' instead of 'w' to accommodate your fav K-pop/J-pop/Viking music
        with self.saveFile.open("wb") as file_handle:
            file_handle.write(str(song_data_dump).encode())

    def notify_download_completion(self, song_obj: SongObj) -> None:
        """Removes given SongObj from download queue and update .musicDLTrackingFile

        Args:
            song_obj: A song that has been downloaded.
        """

        # Remove song form the list
        if song_obj in self.song_obj_list:
            self.song_obj_list.remove(song_obj)

        # Update the tracking file
        self.backup_to_disk()

    def clear(self) -> None:
        self.song_obj_list = []
        self.saveFile = None
