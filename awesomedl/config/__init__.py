from pathlib import Path
from typing import *

from awesomedl.model import TaskType
from pydantic import BaseModel


class ConfigFile(BaseModel):
    name: str
    path: Path


class ConfigManager(object):
    def __init__(self, ytdl_root: Path):
        self.ytdl_configs = {item.stem: ConfigFile(name=item.stem, path=item)
                             for item in ytdl_root.resolve().iterdir()
                             if item.is_file()}

    def config(self, task: TaskType, profile: Optional[str]) -> Optional[ConfigFile]:
        if task == TaskType.YTDL:
            if profile:
                return self.ytdl_configs.get(profile)
            else:
                return None
        else:
            return None

    def list(self, task: TaskType) -> List[str]:
        if task == TaskType.YTDL:
            return list(self.ytdl_configs.keys())
        else:
            return list()
