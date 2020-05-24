from typing import *
from awesomedl.model import TaskType, TaskStatus
from awesomedl.model.views import SubmittedTaskModel
from asyncio.subprocess import Process, create_subprocess_exec, PIPE
import sys
from awesomedl.config import ConfigManager, ConfigFile

# These classes are for encapsulating how to turn a url into a process


class DownloadTask(object):
    def type(self) -> TaskType:
        pass

    def submitted_task(self) -> SubmittedTaskModel:
        pass

    async def process(self, config: ConfigManager) -> Optional[Process]:
        pass


class YTDLDownloadTask(DownloadTask):
    def __init__(self, task: SubmittedTaskModel):
        self.task = task

    def type(self) -> TaskType:
        return TaskType.YTDL

    def submitted_task(self) -> SubmittedTaskModel:
        return self.task

    async def process(self, config_manager: ConfigManager) -> Optional[Process]:
        args = [self.task.url, "--newline"]

        config_file: Optional[ConfigFile] = config_manager.config(self.type(), self.submitted_task().profile)

        if config_file:
            path = str(config_file.path.resolve())
            args = args + ["--ignore-config", "--config-location", path]

        status = TaskStatus(self.task.status)
        if status is not TaskStatus.CREATED:
            return None
        else:
            # Not a huge fan of this mutable state change, but otherwise this is out of sync with the DB
            self.task.status = TaskStatus.PROCESSING
            process = await create_subprocess_exec(sys.executable, "-m", "youtube_dl", *args, stdout=PIPE)
            return process
