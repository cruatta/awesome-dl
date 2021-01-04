import re
from asyncio import StreamReader
from asyncio.subprocess import Process
from typing import *

from awesomedl.model import *

# [download]   0.7% of 426.81MiB at 312.43KiB/s ETA 23:09
ytdl_download_pattern = "\[download\]\s+(\S+)\s+of\s+(\S+)\s+at\s+(\S+)\s+ETA\s+(\S+)$"


async def get_next_stdout(process: Process) -> str:
    if not process.returncode:
        return await stream_to_str(process.stdout)
    else:
        return "<process completed>"


async def get_next_stderr(process: Process) -> str:
    if not process.returncode:
        return await stream_to_str(process.stderr)
    else:
        return "<process completed>"


async def stream_to_str(sr: Optional[StreamReader]) -> str:
    out: str = bytes.decode(await sr.readline()) if sr else "<no output>"
    return out


def progress_output_parser(c: DownloadTask, stdout: str) -> Optional[TaskProgress]:
    if isinstance(c, YTDLDownloadTask):
        return ytdl_output_progress_parser(stdout)
    else:
        return None


def ytdl_output_progress_parser(stdout: str) -> Optional[TaskProgress]:
    stdout_fixed = stdout.strip().strip("\\n")
    _match = re.match(ytdl_download_pattern, stdout_fixed)
    if _match:
        percent_complete = _match.group(1).strip("%")
        total_size = _match.group(2)
        speed = _match.group(3)
        eta = _match.group(4)
        return TaskProgress(percent_complete, total_size, speed, eta)
    else:
        return None
