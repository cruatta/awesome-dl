from typing import *
from awesomedl.model import SubmittedTaskModel
from asyncio.subprocess import Process, create_subprocess_exec, PIPE
import sys

# These classes are for encapsulating how to turn a url into a process


class DownloadTask(object):
    def cancel(self):
        pass

    def submitted_task(self) -> SubmittedTaskModel:
        pass

    async def process(self) -> Optional[Process]:
        pass


class YTDLDownloadTask(DownloadTask):
    def __init__(self, task: SubmittedTaskModel):
        self.task = task

    def submitted_task(self) -> SubmittedTaskModel:
        return self.task

    def cancel(self):
        self.task.cancelled = True

    async def process(self) -> Optional[Process]:
        args = [self.task.url, "--newline"]
        if self.task.cancelled:
            return None
        else:
            process = await create_subprocess_exec(sys.executable, "-m", "youtube_dl", *args, stdout=PIPE)
            return process
