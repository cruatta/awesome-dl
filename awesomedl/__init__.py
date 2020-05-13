from pydantic import BaseModel
from typing import *


class DownloadTask(BaseModel):
    url: str


