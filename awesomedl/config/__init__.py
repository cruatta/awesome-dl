from pathlib import Path
from typing import *

from awesomedl.model import TaskType
from awesomedl.vars import YTDL_CONFIG_PATH
from pydantic import BaseModel
import os


class ConfigFile(BaseModel):
    name: str
    path: Path


class ConfigManager(object):
    def __init__(self, ytdl_root: Optional[Path]):
        def load_config():
            if ytdl_root is not None:
                return {item.stem: ConfigFile(name=item.stem, path=item)
                        for item in ytdl_root.resolve().iterdir()
                        if item.is_file()}
            else:
                return {}

        self.ytdl_configs: Dict[str, ConfigFile] = load_config()

    @staticmethod
    def default_config_path() -> Path:
        return Path(Path.home(), ".config", "awesome", "ytdl")

    @staticmethod
    def config_path() -> Optional[Path]:
        ytdl_config_path: str = os.environ.get(YTDL_CONFIG_PATH) or str(ConfigManager.default_config_path())
        maybe_path = Path(ytdl_config_path)
        return maybe_path if maybe_path.exists() else None

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
