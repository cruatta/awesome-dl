from pydantic import BaseModel
from typing import *


class DownloadRequest(BaseModel):
    url: str


class SubmittedTask(BaseModel):
    url: str
    uuid: str


class PID(BaseModel):
    uuid: str


def download_to_submitted(d: DownloadRequest, uuid: str) -> SubmittedTask:
    d = {"url": str(d.url), "uuid": str(uuid)}
    return SubmittedTask(**d)
