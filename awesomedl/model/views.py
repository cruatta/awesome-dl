from typing import *

from pydantic import BaseModel


class DownloadRequestModel(BaseModel):
    url: str
    profile: Optional[str]


class SubmittedTaskModel(BaseModel):
    uuid: str
    url: str
    submitted_ts: str
    status: int
    profile: Optional[str] = None

    @staticmethod
    def create(url: str, uuid: str, submitted_ts: str, status: int, profile: Optional[str]):
        return SubmittedTaskModel(url=url, uuid=uuid, submitted_ts=submitted_ts, status=status, profile=profile)


class ProgressModel(BaseModel):
    percent_complete: str
    total_size: str
    speed: str
    eta: str

    @staticmethod
    def create(percent_complete: str, total_size: str, speed: str, eta: str):
        d = {"percent_complete": percent_complete, "total_size": total_size, "speed": speed, "eta": eta}
        return ProgressModel(**d)

    @staticmethod
    def na():
        return ProgressModel.create("N/A", "N/A", "N/A", "N/A")


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
