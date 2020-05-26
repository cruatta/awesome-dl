from dataclasses import dataclass
from awesomedl.model import TaskType
from awesomedl.model.views import SubmittedTaskModel

# These classes are for encapsulating how to turn a url into a process


@dataclass()
class DownloadTask(object):
    submitted_task: SubmittedTaskModel
    type: TaskType


@dataclass()
class YTDLDownloadTask(DownloadTask):
    submitted_task: SubmittedTaskModel
    type: TaskType = TaskType.YTDL
