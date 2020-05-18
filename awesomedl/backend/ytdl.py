from awesomedl.model import *
from awesomedl.task import YTDLDownloadTask
from awesomedl.task.queue import TaskQueue
import uuid
from datetime import datetime


class YTDLBackend(object):

    def __init__(self, task_queue: TaskQueue):
        self.task_queue: TaskQueue = task_queue

    async def add(self, task: DownloadRequestModel) -> SubmittedTaskModel:
        sub = SubmittedTaskModel.create(task, str(uuid.uuid4()), str(datetime.now()))
        down = YTDLDownloadTask(sub)
        await self.task_queue.add(down)
        return sub