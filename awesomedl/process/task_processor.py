from asyncio.subprocess import PIPE, Process, create_subprocess_exec
from typing import *
import sys

from awesomedl.config import ConfigManager, ConfigFile
from awesomedl.model import TaskStatus, TaskType
from awesomedl.model.task import DownloadTask, YTDLDownloadTask


class TaskProcessor(object):

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    async def process(self, task: DownloadTask) -> Optional[Process]:
        if task.type() == TaskType.YTDL:
            return await self.ytdl_process(task)
        else:
            return None

    async def ytdl_process(self, task: YTDLDownloadTask) -> Optional[Process]:
        add_args = [task.submitted_task().url, "--newline"]

        config_file: Optional[ConfigFile] = self.config_manager.config(task.type(), task.submitted_task().profile)

        if config_file:
            path = str(config_file.path.resolve())
            add_args = add_args + ["--ignore-config", "--config-location", path]

        status = TaskStatus(task.submitted_task().status)
        if status is not TaskStatus.PROCESSING:
            return None
        else:
            process = await create_subprocess_exec(sys.executable, "-m", "youtube_dl", *add_args, stdout=PIPE)
            return process
