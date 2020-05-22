from awesomedl.model.task import *
from asyncio.subprocess import Process
from asyncio.queues import Queue
from asyncio import create_task, sleep
from typing import *
from awesomedl.datasource.sqlite import SQLiteDatasource


class TaskQueue(object):

    def __init__(self, db: SQLiteDatasource):
        self.db = db
        self._workers = list()
        self._running_tasks: Dict[int, (DownloadTask, Process)] = dict()
        self._init_wait = 1

        for i in range(1):
            worker = create_task(self._worker(i, self._init_wait, self.db))
            self._workers.append(worker)

    def kill_workers(self):
        for _id, worker in enumerate(self._workers):
            task: Optional[Tuple[DownloadTask, Process]] = self._running_tasks.get(_id)
            if task is not None:
                task[1].kill()
            worker.cancel()

    def view_running_tasks(self) -> Iterator[Tuple[DownloadTask, Process]]:
        return iter(list(self._running_tasks.values()))

    async def view_task_queue(self) -> Iterator[DownloadTask]:
        queue = await self.db.list_all()
        return iter(queue)

    async def add(self, task: DownloadTask):
        await self.db.put(task)

    async def cancel(self, _uuid: str) -> bool:
        for running_task in self.view_running_tasks():
            if _uuid == running_task[0].submitted_task().uuid:
                try:
                    running_task[1].terminate()
                except ProcessLookupError:
                    pass
                except Exception as e:
                    raise e
        for queued_task in await self.db.list_all():
            if _uuid == queued_task.submitted_task().uuid:
                await self.db.cancel(queued_task.submitted_task().uuid)
                return True
        return False

    @staticmethod
    def _calc_next_wait(wait: int) -> int:
        return min(10, wait + 1)

    async def _worker(self, _id: int, init_wait: int, db: SQLiteDatasource):
        wait_time = init_wait

        while True:
            wait_time = self._calc_next_wait(wait_time)
            print("Waiting for {}".format(wait_time))
            await sleep(wait_time)
            maybe_task: DownloadTask = await db.get()
            if maybe_task is not None:
                process = await maybe_task.process()
                self._running_tasks[_id] = (maybe_task, process)

                if process:
                    print("Worker id: {} waiting on task".format(_id))
                    await process.wait()

                del(self._running_tasks[_id])
                await db.mark_done(maybe_task.submitted_task().uuid)
                wait_time = init_wait


