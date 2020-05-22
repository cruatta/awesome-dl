from awesomedl.model.task import *
from asyncio.subprocess import Process
from asyncio import Lock
from asyncio import create_task, sleep
from typing import *
from awesomedl.datasource.sqlite import SQLiteDatasource


class TaskQueue(object):

    def __init__(self, db: SQLiteDatasource):
        self._db = db
        self._lock = Lock()
        self._num_workers = 4
        self._workers = list()
        self._running_tasks: Dict[int, (DownloadTask, Process)] = dict()
        self._init_wait = 1

        for i in range(self._num_workers):
            worker = create_task(self._worker(i, self._init_wait, self._db))
            self._workers.append(worker)

    def kill_workers(self):
        for _id, worker in enumerate(self._workers):
            task: Optional[Tuple[DownloadTask, Process]] = self._running_tasks.get(_id)
            if task is not None:
                task[1].terminate()
            worker.cancel()

    def view_running_tasks(self) -> Iterator[Tuple[DownloadTask, Process]]:
        return iter(list(self._running_tasks.values()))

    async def view_task_queue(self) -> List[DownloadTask]:
        return await self._db.list_all()

    async def add(self, task: DownloadTask):
        await self._db.put(task)

    async def cleanup(self):
        await self._db.cleanup()

    async def cancel(self, _uuid: str) -> bool:
        for running_task in self.view_running_tasks():
            if _uuid == running_task[0].submitted_task().uuid:
                try:
                    running_task[1].terminate()
                except ProcessLookupError:
                    pass
                except Exception as e:
                    raise e
        for queued_task in await self._db.list_all():
            if _uuid == queued_task.submitted_task().uuid:
                await self._db.cancel(queued_task.submitted_task().uuid)
                return True
        return False

    @staticmethod
    def _calc_next_wait(wait: int) -> int:
        return min(5, wait + 1)

    async def _worker(self, _id: int, init_wait: int, db: SQLiteDatasource):
        wait_time = init_wait

        while True:
            wait_time = self._calc_next_wait(wait_time)
            print("Worker id: {} - Waiting for {}".format(_id, wait_time))
            await sleep(wait_time)
            async with self._lock:
                maybe_task: DownloadTask = await db.get()
            if maybe_task is not None:
                process = await maybe_task.process()
                self._running_tasks[_id] = (maybe_task, process)

                if process:
                    print("Worker id: {} - Waiting on task".format(_id))
                    await process.wait()

                del (self._running_tasks[_id])
                await db.mark_done(maybe_task.submitted_task().uuid)
                wait_time = init_wait


