import sys

from awesomedl.model import TaskType
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
        self.executable: str = sys.executable
        self.args = ["-m", "youtube_dl"]

    def type(self) -> TaskType:
        return TaskType.YTDL

    def submitted_task(self) -> SubmittedTaskModel:
        return self.task
