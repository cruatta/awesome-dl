from awesomedl.model import *
from awesomedl.logic.ytdl import cli_dl_output_parser
from awesomedl.tasks import YTDLDownloadTask
from awesomedl.tasks.queue import TaskQueue
from asyncio import StreamReader, create_task
from typing import *
import uuid
from datetime import datetime


class YTDL(object):

    def __init__(self, task_queue: TaskQueue):
        self.task_queue: TaskQueue = task_queue

    @staticmethod
    async def _stream_to_str(sr: Optional[StreamReader]) -> str:
        out: str = bytes.decode(await sr.readline()) if sr else "<no output>"
        return out

    async def add(self, task: DownloadRequest) -> SubmittedTask:
        sub = SubmittedTask.create(task, str(uuid.uuid4()), str(datetime.now()))
        down = YTDLDownloadTask(sub)
        await self.task_queue.add(down)
        return sub

    def tasks(self) -> List[SubmittedTask]:
        return [f.submitted_task() for f in self.task_queue.view_task_queue()]

    async def running(self) -> List[TaskProgress]:
        _running = list()
        for f in self.task_queue.view_worker_tasks():
            if f[1].pid:
                maybe_progress: Optional[ProgressModel] = cli_dl_output_parser(await self._stream_to_str(f[1].stdout))
                progress: ProgressModel = maybe_progress if maybe_progress else ProgressModel.na()
                _running.append(TaskProgress.create(f[0].submitted_task(), progress))
        return _running

    async def stdout(self, _uuid: str) -> List[StdoutModel]:
        for f in self.task_queue.view_worker_tasks():
            if f[0].submitted_task().uuid == _uuid:
                stdout: str = await self._stream_to_str(f[1].stdout)
                return list(StdoutModel.create(_uuid, stdout))
        return list()

    def cancel(self, pid: UUID) -> bool:
        for f in self.task_queue.view_worker_tasks():
            if pid.uuid == f[0].submitted_task().uuid:
                try:
                    f[1].terminate()
                except ProcessLookupError:
                    return True
                except Exception as e:
                    raise e
                return True
        return False
