from awesomedl.task import *
from asyncio.subprocess import Process
from asyncio.queues import Queue
from asyncio import create_task
from typing import *


class TaskQueue(object):

    def __init__(self):
        self._workers = list()
        self._task_queue: Queue[DownloadTask] = Queue()
        self._running_tasks: Dict[int, (DownloadTask, Process)] = dict()
        for i in range(1):
            worker = create_task(self._worker(i, self._task_queue))
            self._workers.append(worker)

    def view_running_tasks(self) -> Iterator[Tuple[DownloadTask, Process]]:
        return iter(list(self._running_tasks.values()))

    def view_task_queue(self) -> Iterator[DownloadTask]:
        return iter(list(self._task_queue._queue))

    async def add(self, task: DownloadTask):
        await self._task_queue.put(task)

    def cancel(self, _uuid: str) -> bool:
        for running_task in self.view_running_tasks():
            if _uuid == running_task[0].submitted_task().uuid:
                try:
                    running_task[1].terminate()
                except ProcessLookupError:
                    running_task[0].cancel()
                    return True
                except Exception as e:
                    raise e
                running_task[0].cancel()
                return True
        for queued_task in self.view_task_queue():
            if _uuid == queued_task.submitted_task().uuid:
                queued_task.cancel()
                return True
        return False

    async def _worker(self, _id: int, _queue: Queue):
        while True:
            task: DownloadTask = await _queue.get()
            process = await task.process()
            self._running_tasks[_id] = (task, process)

            if process:
                await process.wait()

            del(self._running_tasks[_id])
            _queue.task_done()


