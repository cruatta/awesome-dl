from awesomedl.model import *
from typing import *
import re


# [download]   0.7% of 426.81MiB at 312.43KiB/s ETA 23:09
cli_download_pattern = "\[download\]\s+(\S+)\s+of\s+(\S+)\s+at\s+(\S+)\s+ETA\s+(\S+)$"


def cli_dl_output_parser(stdout: str) -> Optional[ProgressModel]:
    stdout_fixed = stdout.strip().strip("\\n")
    _match = re.match(cli_download_pattern, stdout_fixed)
    if _match:
        percent_complete = _match.group(1)
        total_size = _match.group(2)
        speed = _match.group(3)
        eta = _match.group(4)
        return ProgressModel.create(percent_complete, total_size, speed, eta)
    else:
        return None
