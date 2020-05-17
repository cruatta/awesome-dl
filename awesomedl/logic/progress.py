from awesomedl.model import *
from awesomedl.task import *
from typing import *
import re


# [download]   0.7% of 426.81MiB at 312.43KiB/s ETA 23:09
ytdl_download_pattern = "\[download\]\s+(\S+)\s+of\s+(\S+)\s+at\s+(\S+)\s+ETA\s+(\S+)$"


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
