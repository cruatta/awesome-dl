from awesomedl.model import *
from typing import *
import re


# [download]   0.7% of 426.81MiB at 312.43KiB/s ETA 23:09
cli_download_pattern = "^\w+\[download\]\s+(\S+)\s+of\s+(\S+)\s+at\s+(\S+)\s+ETA\s+(\S+)\w+$"


def cli_download_output_parser(stdout: str) -> Optional[ProgressModel]:
    _match = re.match(cli_download_pattern, stdout)
    if _match:
        percent_complete = _match.group(1)
        total_size = _match.group(2)
        speed = _match.group(3)
        eta = _match.group(4)
        return to_progress_model(percent_complete, total_size, speed, eta)
    else:
        return None
