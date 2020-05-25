import re
from asyncio import StreamReader
from typing import *

from awesomedl.model.task import YTDLDownloadTask, DownloadTask
from awesomedl.model.views import ProgressModel

ytdl_download_pattern = "\[download\]\s+(\S+)\s+of\s+(\S+)\s+at\s+(\S+)\s+ETA\s+(\S+)$"


async def stream_to_str(sr: Optional[StreamReader]) -> str:
    out: str = bytes.decode(await sr.readline()) if sr else "<no output>"
    return out


def progress_output_parser(c: DownloadTask, stdout: str) -> Optional[ProgressModel]:
    if isinstance(c, YTDLDownloadTask):
        return ytdl_output_progress_parser(stdout)
    else:
        return None


def ytdl_output_progress_parser(stdout: str) -> Optional[ProgressModel]:
    stdout_fixed = stdout.strip().strip("\\n")
    _match = re.match(ytdl_download_pattern, stdout_fixed)
    if _match:
        percent_complete = _match.group(1)
        total_size = _match.group(2)
        speed = _match.group(3)
        eta = _match.group(4)
        return ProgressModel.create(percent_complete, total_size, speed, eta)
    else:
        return None
