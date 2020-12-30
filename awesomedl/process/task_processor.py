from asyncio.subprocess import PIPE, Process, create_subprocess_exec
from typing import *
import sys

from awesomedl.config import ConfigManager, ConfigFile
from awesomedl.model import TaskStatus, DownloadTask, YTDLDownloadTask, TaskType


class TaskProcessorException(Exception):
    def __init__(self, message: str):
        self.message = message


class TaskProcessor(object):

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager

    def ytdl_args(self, task: YTDLDownloadTask) -> Union[TaskProcessorException, List[str]]:
        status = TaskStatus(task.submitted_task.status)
        profile = task.submitted_task.profile
        config_file: Optional[ConfigFile] = self.config_manager.config(task.type, profile)

        if status is not TaskStatus.Processing:
            return TaskProcessorException("Task is in the wrong status: {}".format(status))
        if config_file is None and profile is not None:
            return TaskProcessorException("Missing profile: {}".format(profile))
        else:
            args = ["-m", "youtube_dl", task.submitted_task.url, "--newline"]
            if config_file:
                path = str(config_file.path.resolve())
                args = args + ["--ignore-config", "--config-location", path]
            return args

    async def process(self, task: DownloadTask) -> Union[TaskProcessorException, Process]:
        if isinstance(task, YTDLDownloadTask):
            args = self.ytdl_args(task)
            if isinstance(args, TaskProcessorException):
                return args
            else:
                return await create_subprocess_exec(sys.executable, *args, stdout=PIPE)
        else:
            return TaskProcessorException("Invalid task type")
