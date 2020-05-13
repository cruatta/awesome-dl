from youtube_dl import YoutubeDL
from awesomedl.model import *
from concurrent.futures import ThreadPoolExecutor, Future, ProcessPoolExecutor
from dill import pickle
from typing import *
import uuid


class YTDL(object):

    def __init__(self):
        self.task_futures: List[(Future[SubmittedTask], SubmittedTask)] = list()
        self.ytdl_pool: ThreadPoolExecutor = ThreadPoolExecutor(4)
        self.ytdl: YoutubeDL = YoutubeDL()

    def add(self, task: DownloadRequest) -> SubmittedTask:
        sub = download_to_submitted(task, str(uuid.uuid4()))
        print(sub)
        future = self.ytdl_pool.submit(self.ytdl.download, [sub.url])
        self.task_futures.append((future, sub))
        return sub

    def tasks(self) -> List[SubmittedTask]:
        return [f[1] for f in self.task_futures]

    def running(self) -> List[SubmittedTask]:
        return [f[1] for f in self.task_futures if f[0].running()]

    def cancel(self, pid: PID) -> bool:
        for f in self.task_futures:
            if pid.uuid == f[1].uuid:
                return f[0].set_exception()
        return False
