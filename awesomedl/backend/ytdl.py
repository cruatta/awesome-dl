import uuid
from datetime import datetime
from awesomedl.model import DownloadRequestModel, SubmittedTaskModel, YTDLDownloadTask, TaskStatus
from awesomedl.queue import TaskQueue


class YTDLBackend(object):

    def __init__(self, task_queue: TaskQueue):
        self.task_queue: TaskQueue = task_queue

    async def add(self, task: DownloadRequestModel) -> SubmittedTaskModel:
        sub = SubmittedTaskModel.create(task.url, str(uuid.uuid4()), str(datetime.now()), TaskStatus.Created,
                                        task.profile)
        down = YTDLDownloadTask(sub)
        await self.task_queue.add(down)
        return sub
