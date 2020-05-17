from typing import *
from awesomedl.model import SubmittedTaskModel
from asyncio.subprocess import Process, create_subprocess_exec, PIPE
import sys

# These classes are for encapsulating how to turn a url into a process


class DownloadTask(object):
    def submitted_task(self) -> SubmittedTaskModel:
        raise Exception("Unimplemented")

    async def process(self) -> Process:
        raise Exception("Unimplemented")


class YTDLDownloadTask(DownloadTask):
    def __init__(self, sub_task: SubmittedTaskModel):
        self.sub_task = sub_task

    def submitted_task(self) -> SubmittedTaskModel:
        return self.sub_task

    async def process(self) -> Process:
        args = [self.sub_task.url, "--newline"]
        process = await create_subprocess_exec(sys.executable, "-m", "youtube_dl", *args, stdout=PIPE)
        return process
