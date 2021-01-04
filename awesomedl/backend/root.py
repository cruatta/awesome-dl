from awesomedl.model import *
from awesomedl.queue import TaskQueue


class RootBackend(object):

    def __init__(self, task_queue: TaskQueue):
        self.task_queue: TaskQueue = task_queue

    async def all(self) -> List[SubmittedTaskModel]:
        tasks_queued = await self.task_queue.view_all()
        return [task.submitted_task for task in tasks_queued]

    async def cancel(self, _uuid: UUIDModel) -> List[CancelModel]:
        result = await self.task_queue.cancel(_uuid.uuid)
        if result is not None:
            return [CancelModel.create(_uuid.uuid, result)]
        else:
            return []

    async def cancel_all(self) -> List[CancelModel]:
        results = await self.task_queue.cancel_all()
        return CancelModel.create_many(results)

    async def cleanup(self):
        await self.task_queue.cleanup()
        return ResultModel.create(ok=True)

    async def retry_processed_tasks(self):
        await self.task_queue.retry_processed_tasks()
        return ResultModel.create(ok=True)

    async def retry_task(self, _uuid: UUIDModel):
        await self.task_queue.retry(_uuid.uuid)
        return ResultModel.create(ok=True)

    async def running(self) -> List[SubmittedTaskModel]:
        return [running_task.submitted_task for running_task in self.task_queue.view_running_tasks()]

    async def progress(self, _uuid: UUIDModel) -> List[ProgressModel]:
        maybe_result = await self.task_queue.view_task(_uuid.uuid)
        if maybe_result:
            submitted = maybe_result[0].submitted_task
            task_progress = maybe_result[1]
            progress_model = ProgressModel.create(submitted.status, task_progress.percent_complete,
                                                  task_progress.total_size, task_progress.speed, task_progress.eta)
            return [progress_model]
        else:
            return list()
