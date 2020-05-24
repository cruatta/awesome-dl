from awesomedl.model.task import YTDLDownloadTask
from awesomedl.model.views import DownloadRequestModel, SubmittedTaskModel
from awesomedl.queue import TaskQueue
from awesomedl.config.__init__ import *
import uuid
from datetime import datetime
from awesomedl.model.task import TaskStatus


class YTDLBackend(object):

    def __init__(self, task_queue: TaskQueue):
        self.task_queue: TaskQueue = task_queue

    async def add(self, task: DownloadRequestModel) -> SubmittedTaskModel:
        sub = SubmittedTaskModel.create(task.url, str(uuid.uuid4()), str(datetime.now()), TaskStatus.CREATED,
                                        task.profile)
        down = YTDLDownloadTask(sub)
        await self.task_queue.add(down)
        return sub
