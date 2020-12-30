from awesomedl.model import *
from awesomedl.queue import TaskQueue


class RootBackend(object):

    def __init__(self, task_queue: TaskQueue):
        self.task_queue: TaskQueue = task_queue

    async def all(self) -> List[SubmittedTaskModel]:
        tasks_queued = await self.task_queue.view_all()
        return [task.submitted_task for task in tasks_queued]

    async def cancel(self, _uuid: UUIDModel) -> bool:
        return await self.task_queue.cancel(_uuid.uuid)

    async def cleanup(self):
        return await self.task_queue.cleanup()

    async def retry_processed_tasks(self):
        return await self.task_queue.retry_processed_tasks()

    async def retry_task(self, _uuid: UUIDModel):
        return await self.task_queue.retry(_uuid.uuid)

    async def running(self) -> List[SubmittedTaskModel]:
        return [running_task.submitted_task for running_task in self.task_queue.view_running_tasks()]

    async def progress(self, _uuid: UUIDModel) -> List[TaskProgressModel]:
        maybe_result = await self.task_queue.view_task(_uuid.uuid)
        if maybe_result:
            submitted = maybe_result[0].submitted_task
            task_progress = maybe_result[1]
            progress_model = ProgressModel.create(submitted.status.name, task_progress.percent_complete,
                                                  task_progress.total_size, task_progress.speed, task_progress.eta)
            return [TaskProgressModel.create(submitted, progress_model)]
        else:
            return list()
