from pydantic import BaseModel
from typing import *


class DownloadRequest(BaseModel):
    url: str


# TODO: Add date
class SubmittedTask(BaseModel):
    uuid: str
    url: str
    start_time: str


class ProgressModel(BaseModel):
    percent_complete: str
    total_size: str
    speed: str
    eta: str


class PID(BaseModel):
    uuid: str


class StdoutModel(BaseModel):
    uuid: str
    stdout: str


def to_stdout_model(uuid: str, stdout: str) -> StdoutModel:
    d = {"uuid": uuid, "stdout": stdout}
    return StdoutModel(**d)


def to_progress_model(percent_complete: str, total_size: str, speed: str, eta: str) -> ProgressModel:
    d = {"percent_complete": percent_complete, "total_size": total_size, "speed": speed, "eta": eta}
    return ProgressModel(**d)


def to_submitted_task_model(d: DownloadRequest, uuid: str, start_time: str) -> SubmittedTask:
    d = {"url": str(d.url), "uuid": str(uuid), "start_time": start_time}
    return SubmittedTask(**d)
