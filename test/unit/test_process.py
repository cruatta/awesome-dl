from awesomedl.process.output import ytdl_output_progress_parser
from awesomedl.process.task_processor import TaskProcessor, TaskProcessorException
from awesomedl.config import ConfigManager
from awesomedl.model.task import YTDLDownloadTask, SubmittedTaskModel
from awesomedl.model import TaskStatus
import tempfile
from pathlib import Path


def test_ytdl_args():
    with tempfile.TemporaryDirectory() as tmp:
        c = ConfigManager(ytdl_root=Path(tmp))
        task_processor = TaskProcessor(c)
        url = "https://youtube-dl"
        task = YTDLDownloadTask(SubmittedTaskModel.create("https://youtube-dl", "uuid", "2019-01-01 09:19:20",
                                                          TaskStatus.PROCESSING, None))
        args = task_processor.ytdl_args(task)
        assert args is not None
        assert args == ["-m", "youtube_dl", url, "--newline"]


def test_ytdl_args_wrong_status():
    with tempfile.TemporaryDirectory() as tmp:
        c = ConfigManager(ytdl_root=Path(tmp))
        task_processor = TaskProcessor(c)
        task = YTDLDownloadTask(SubmittedTaskModel.create("https://youtube-dl", "uuid", "2019-01-01 09:19:20",
                                                          TaskStatus.DONE, None))
        args = task_processor.ytdl_args(task)
        assert isinstance(args, TaskProcessorException)


def test_ytdl_args_with_config():
    with tempfile.TemporaryDirectory() as tmp_dir:
        with tempfile.NamedTemporaryFile(dir=tmp_dir) as tmp_file:
            path = Path(tmp_file.name)
            url = "https://youtube-dl"
            c = ConfigManager(ytdl_root=Path(tmp_dir))
            task_processor = TaskProcessor(c)
            task = YTDLDownloadTask(SubmittedTaskModel.create(url, "uuid", "2019-01-01 09:19:20",
                                                              TaskStatus.PROCESSING, path.name))
            args = task_processor.ytdl_args(task)
            assert args == ["-m", "youtube_dl", url, "--newline", "--ignore-config", "--config-location",
                            str(path.resolve())]


def test_ytdl_args_with_missing_config():
    with tempfile.TemporaryDirectory() as tmp_dir:
        with tempfile.NamedTemporaryFile(dir=tmp_dir) as tmp_file:
            path = Path(tmp_file.name)
            profile = "fakefakefakefakefakefake"

            assert path.name != profile

            url = "https://youtube-dl"
            c = ConfigManager(ytdl_root=Path(tmp_dir))
            task_processor = TaskProcessor(c)
            task = YTDLDownloadTask(SubmittedTaskModel.create(url, "uuid", "2019-01-01 09:19:20",
                                                              TaskStatus.PROCESSING, profile))
            args = task_processor.ytdl_args(task)
            assert isinstance(args, TaskProcessorException)


def test_ytdl_output_progress_parser():
    out = " [download]   0.7% of 426.81MiB at 312.43KiB/s ETA 23:09 "
    model = ytdl_output_progress_parser(out)
    if model:
        assert model.speed == "312.43KiB/s"
        assert model.total_size == "426.81MiB"
        assert model.percent_complete == "0.7%"
        assert model.eta == "23:09"
    else:
        assert False


def test_invalid_ytdl_output_progress_parser():
    out = "[download]   10.0% This is invalid output"
    model = ytdl_output_progress_parser(out)
    if model:
        assert False
    else:
        assert True

