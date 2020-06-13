from awesomedl.process.output import progress_output_parser, get_next_stdout
from awesomedl.model.views import *
from awesomedl.queue import TaskQueue


class RootBackend(object):

    def __init__(self, task_queue: TaskQueue):
        self.task_queue: TaskQueue = task_queue

    async def queued(self) -> List[SubmittedTaskModel]:
        tasks_queued = await self.task_queue.view_task_queue()
        return [task.submitted_task for task in tasks_queued]

    async def cancel(self, _uuid: UUIDModel) -> bool:
        return await self.task_queue.cancel(_uuid.uuid)

    async def cleanup(self):
        return await self.task_queue.cleanup()

    async def retry_processed_tasks(self):
        return await self.task_queue.retry_processed_tasks()

    async def retry_task(self, _uuid: UUIDModel):
        return await self.task_queue.retry(_uuid.uuid)

    async def running(self) -> List[TaskProgressModel]:
        _running = list()
        for running_task in self.task_queue.view_running_tasks():
            maybe_progress: Optional[ProgressModel] = progress_output_parser(
                running_task[0], await get_next_stdout(running_task[1]))
            progress: ProgressModel = maybe_progress if maybe_progress else ProgressModel.na()
            _running.append(TaskProgressModel.create(running_task[0].submitted_task, progress))
        return _running

    async def stdout(self, _uuid: UUIDModel) -> List[StdoutModel]:
        for f in self.task_queue.view_running_tasks():
            if f[0].submitted_task.uuid == _uuid:
                stdout: str = await get_next_stdout(f[1])
                return list(StdoutModel.create(_uuid.uuid, stdout))
        return list()
