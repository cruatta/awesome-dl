from awesomedl.model import *
from awesomedl.logic.output import progress_output_parser, stream_to_str
from awesomedl.task.queue import TaskQueue
from typing import *


class RootBackend(object):

    def __init__(self, task_queue: TaskQueue):
        self.task_queue: TaskQueue = task_queue

    def queued(self) -> List[SubmittedTaskModel]:
        return [f.submitted_task() for f in self.task_queue.view_task_queue()]

    def cancel(self, _uuid: UUIDModel) -> bool:
        return self.task_queue.cancel(_uuid.uuid)

    async def running(self) -> List[TaskProgressModel]:
        _running = list()
        for running_task in self.task_queue.view_running_tasks():
            if running_task[1].pid:
                maybe_progress: Optional[ProgressModel] = progress_output_parser(
                    running_task[0], await stream_to_str(running_task[1].stdout))
                progress: ProgressModel = maybe_progress if maybe_progress else ProgressModel.na()
                _running.append(TaskProgressModel.create(running_task[0].submitted_task(), progress))
        return _running

    async def stdout(self, _uuid: str) -> List[StdoutModel]:
        for f in self.task_queue.view_running_tasks():
            if f[0].submitted_task().uuid == _uuid:
                stdout: str = await stream_to_str(f[1].stdout)
                return list(StdoutModel.create(_uuid, stdout))
        return list()