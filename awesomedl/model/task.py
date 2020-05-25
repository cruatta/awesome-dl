import sys
from asyncio.subprocess import PIPE, Process, create_subprocess_exec
from typing import *

from awesomedl.config import ConfigFile, ConfigManager
from awesomedl.model import TaskStatus, TaskType
from awesomedl.model.views import SubmittedTaskModel

# These classes are for encapsulating how to turn a url into a process


class DownloadTask(object):
    def type(self) -> TaskType:
        pass

    def submitted_task(self) -> SubmittedTaskModel:
        pass


class YTDLDownloadTask(DownloadTask):
    def __init__(self, task: SubmittedTaskModel):
        self.task = task

    def type(self) -> TaskType:
        return TaskType.YTDL

    def submitted_task(self) -> SubmittedTaskModel:
        return self.task

