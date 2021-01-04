from dataclasses import dataclass
from typing import *
from pydantic import BaseModel
from enum import Enum, IntEnum, unique


@unique
class TaskStatus(IntEnum):
    Created = 0
    Processing = 1
    Cancelled = 2
    Done = 3
    Failed = 4


class DownloadRequestModel(BaseModel):
    url: str
    profile: Optional[str] = None


class SubmittedTaskModel(BaseModel):
    uuid: str
    url: str
    submitted_ts: str
    status: TaskStatus
    profile: Optional[str] = None

    @staticmethod
    def create(url: str, uuid: str, submitted_ts: str, status: TaskStatus, profile: Optional[str]):
        return SubmittedTaskModel(url=url, uuid=uuid, submitted_ts=submitted_ts, status=status, profile=profile)


class ProgressModel(BaseModel):
    status: int
    percent_complete: str
    total_size: str
    speed: str
    eta: str

    @staticmethod
    def create(status: int, percent_complete: str, total_size: str, speed: str, eta: str):
        d = {"status": status, "percent_complete": percent_complete, "total_size": total_size, "speed": speed,
             "eta": eta}
        return ProgressModel(**d)


class TaskProgressModel(BaseModel):
    task: SubmittedTaskModel
    progress: ProgressModel

    @staticmethod
    def create(task: SubmittedTaskModel, progress: ProgressModel):
        d = {"task": task, "progress": progress}
        return TaskProgressModel(**d)


class UUIDModel(BaseModel):
    uuid: str


class StdoutModel(BaseModel):
    uuid: str
    stdout: str

    @staticmethod
    def create(uuid: str, stdout: str):
        d = {"uuid": uuid, "stdout": stdout}
        return StdoutModel(**d)


class ResultModel(BaseModel):
    ok: bool
    output: Optional[str]

    @staticmethod
    def create(ok: bool, output: Optional[str] = None):
        return ResultModel(ok=ok, output=output)


class CancelModel(BaseModel):
    uuid: str
    success: bool

    @staticmethod
    def create(uuid: str, success: bool):
        return CancelModel(uuid=uuid, success=success)

    @staticmethod
    def create_many(values: Dict[str, bool]):
        result: List[CancelModel] = list()
        for key, value in values.items():
            result = result + [CancelModel.create(key, value)]
        return result


class HealthModel(BaseModel):
    name: str
    version: str

    @staticmethod
    def create(name: str, version: str):
        return HealthModel(name=name, version=version)


# These classes are for encapsulating how to turn a url into a process

@unique
class TaskType(Enum):
    YTDL = "ytdl"


@dataclass()
class TaskProgress(object):
    percent_complete: str
    total_size: str
    speed: str
    eta: str

    @staticmethod
    def na():
        return TaskProgress("N/A", "N/A", "N/A", "N/A")

    @staticmethod
    def complete():
        return TaskProgress("100", "N/A", "N/A", "N/A")


@dataclass()
class DownloadTask(object):
    submitted_task: SubmittedTaskModel
    type: TaskType


@dataclass()
class YTDLDownloadTask(DownloadTask):
    submitted_task: SubmittedTaskModel
    type: TaskType = TaskType.YTDL
