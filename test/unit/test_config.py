from awesomedl.config import ConfigManager, ConfigFile
from awesomedl.model import TaskType
import tempfile
from pathlib import Path


def test_config():
    with tempfile.TemporaryDirectory() as tmp_dir:
        with tempfile.NamedTemporaryFile(dir=tmp_dir) as tmp_file:
            path = Path(tmp_file.name)
            name = path.name
            c = ConfigManager(ytdl_root=Path(tmp_dir))

            assert c.config(TaskType.YTDL, name) == ConfigFile(name=name, path=path)
            assert c.list(TaskType.YTDL) == [name]


def test_wrong_config():
    with tempfile.TemporaryDirectory() as tmp_dir:
        with tempfile.NamedTemporaryFile(dir=tmp_dir) as tmp_file:
            path = Path(tmp_file.name)
            name = path.name
            c = ConfigManager(ytdl_root=Path(tmp_dir))

            assert c.config(TaskType.YTDL, "wrongwrongwrong") is None
            assert c.list(TaskType.YTDL) == [name]


def test_no_config():
    with tempfile.TemporaryDirectory() as tmp_dir:
        name = 'whatever'
        c = ConfigManager(ytdl_root=Path(tmp_dir))

        assert c.config(TaskType.YTDL, name) is None
