from awesomedl.config import ConfigManager, ConfigFile
from awesomedl.model import TaskType
import tempfile
from pathlib import Path
import os
from awesomedl.vars import YTDL_CONFIG_PATH


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


def test_missing_config():
    with tempfile.TemporaryDirectory() as tmp_dir:
        name = 'whatever'
        c = ConfigManager(ytdl_root=Path(tmp_dir))

        assert c.config(TaskType.YTDL, name) is None


def test_no_config():
    with tempfile.TemporaryDirectory() as tmp_dir:
        name = 'whatever'
        c = ConfigManager(ytdl_root=None)
        assert c.ytdl_configs == {}


def test_config_path():
    with tempfile.TemporaryDirectory() as tmp_dir:
        with tempfile.NamedTemporaryFile(dir=tmp_dir) as tmp_file:
            os.environ[YTDL_CONFIG_PATH] = tmp_file.name
            c = ConfigManager.config_path()
            assert c is not None
            assert str(c) == tmp_file.name


def test_config_path_invalid():
    with tempfile.TemporaryDirectory() as tmp_dir:
        with tempfile.NamedTemporaryFile(dir=tmp_dir) as tmp_file:
            os.environ[YTDL_CONFIG_PATH] = "/yeehaw"
            c = ConfigManager.config_path()
            assert c is None


def test_config_path_default():
    if os.environ[YTDL_CONFIG_PATH] is not None: 
        del os.environ[YTDL_CONFIG_PATH]
    
    ConfigManager.default_config_path().mkdir(parents=True, exist_ok=True)
    
    c = ConfigManager.config_path()
    assert c is not None
    assert c == ConfigManager.default_config_path()
    ConfigManager.default_config_path().rmdir()