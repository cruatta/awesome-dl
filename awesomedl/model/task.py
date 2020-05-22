from typing import *
from awesomedl.model.views import SubmittedTaskModel
from asyncio.subprocess import Process, create_subprocess_exec, PIPE
import sys
from enum import IntEnum, Enum, unique

# These classes are for encapsulating how to turn a url into a process


@unique
class TaskStatus(IntEnum):
    PROCESSED = 0
    CANCELLED = 1
    CREATED = 2
    DONE = 3


@unique
class TaskType(Enum):
    YTDL = "ytdl"


class DownloadTask(object):
    def type(self) -> TaskType:
        pass

    def submitted_task(self) -> SubmittedTaskModel:
        pass

    async def process(self) -> Optional[Process]:
        pass


class YTDLDownloadTask(DownloadTask):
    def __init__(self, task: SubmittedTaskModel):
        self.task = task

    def type(self) -> TaskType:
        return TaskType.YTDL

    def submitted_task(self) -> SubmittedTaskModel:
        return self.task

    async def process(self) -> Optional[Process]:
        args = [self.task.url, "--newline"]
        status = TaskStatus(self.task.status)
        if status is not TaskStatus.CREATED:
            return None
        else:
            # Not a huge fan of this mutable state change, but otherwise this is out of sync with the DB
            self.task.status = TaskStatus.PROCESSED
            process = await create_subprocess_exec(sys.executable, "-m", "youtube_dl", *args, stdout=PIPE)
            return process
