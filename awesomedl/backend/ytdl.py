from youtube_dl import YoutubeDL
from awesomedl.model import *
from asyncio.subprocess import Process, create_subprocess_exec, PIPE
from asyncio import StreamReader
from typing import *
import uuid
import sys
from datetime import datetime


class YTDL(object):

    def __init__(self):
        self.task_futures: List[Tuple[Process, SubmittedTask]] = list()
        self.ytdl: YoutubeDL = YoutubeDL()

    @staticmethod
    def _remove_exited(task_futures: List[Tuple[Process, SubmittedTask]]) -> List[Tuple[Process, SubmittedTask]]:
        return [f for f in task_futures if not f[0].returncode]

    async def add(self, task: DownloadRequest) -> SubmittedTask:
        self.task_futures = self._remove_exited(self.task_futures)
        sub = to_submitted_task_model(task, str(uuid.uuid4()), str(datetime.now()))
        # print(sub)
        process: Process = await create_subprocess_exec(sys.executable, "-m", "youtube_dl", sub.url, "--newline", stdout=PIPE)
        self.task_futures.append((process, sub))
        return sub

    def tasks(self) -> List[SubmittedTask]:
        self.task_futures = self._remove_exited(self.task_futures)
        return [f[1] for f in self.task_futures]

    def running(self) -> List[SubmittedTask]:
        self.task_futures = self._remove_exited(self.task_futures)
        return [f[1] for f in self.task_futures if f[0].pid]

    async def stdout(self, _uuid: str) -> List[StdoutModel]:
        self.task_futures = self._remove_exited(self.task_futures)
        for f in self.task_futures:
            if f[1].uuid == _uuid:
                stdout: str = str(await f[0].stdout.readline()) if f[0].stdout else "<no stdout>"
                return list(to_stdout_model(_uuid, stdout))
        return list()

    def cancel(self, pid: PID) -> bool:
        for f in self.task_futures:
            if pid.uuid == f[1].uuid:
                try:
                    f[0].terminate()
                except ProcessLookupError:
                    return True
                except Exception as e:
                    raise e
                return True
        return False
