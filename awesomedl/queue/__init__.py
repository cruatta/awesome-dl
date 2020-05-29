from asyncio import Lock, create_task, sleep
from asyncio.subprocess import Process
from asyncio.tasks import Task
from random import random
from typing import *
from awesomedl.process.task_processor import TaskProcessorException

from awesomedl.process.task_processor import TaskProcessor
from awesomedl.datasource.sqlite import SQLiteDatasource
from awesomedl.model.task import DownloadTask
from awesomedl.model import TaskStatus
from fastapi.logger import logger


class ShutdownMaxWaitTimeException(Exception):
    pass


class TaskQueue(object):

    def __init__(self, db: SQLiteDatasource, task_processor: TaskProcessor):
        self.task_processor = task_processor
        self.db = db
        self._lock: Lock = Lock()
        self._num_workers: int = 4
        self._workers: List[Task] = list()
        self._running_tasks: Dict[int, Tuple[DownloadTask, Process]] = dict()
        self._init_wait: float = 0

        for i in range(self._num_workers):
            worker = create_task(self._worker(i, self._init_wait, self.db))
            self._workers.append(worker)

    async def wait_for_cancellations(self,
                                     max_wait_time: int,
                                     wait_time: int = 0) -> Optional[ShutdownMaxWaitTimeException]:
        total = len(self._workers)
        waiting = len([worker for worker in self._workers if worker.cancelled() is False])

        if waiting == 0:
            logger.info("Worker pool shut down")
            return None
        elif wait_time == max_wait_time:
            ex = ShutdownMaxWaitTimeException()
            return ex
        else:
            logger.warn("Waiting for {} of {} workers to shut down".format(waiting, total))
            await sleep(1)
            return await self.wait_for_cancellations(max_wait_time, wait_time + 1)

    async def kill_workers(self) -> Optional[ShutdownMaxWaitTimeException]:
        for _id, worker in enumerate(self._workers):
            task: Optional[Tuple[DownloadTask, Process]] = self._running_tasks.get(_id)
            if task is not None:
                task[1].kill()
            worker.cancel()

        return await self.wait_for_cancellations(100)

    def view_running_tasks(self) -> Iterator[Tuple[DownloadTask, Process]]:
        return iter([task for task in self._running_tasks.values() if not task[1].returncode])

    async def view_task_queue(self) -> List[DownloadTask]:
        return await self.db.list_all()

    async def add(self, task: DownloadTask):
        await self.db.put(task)

    async def retry(self, _uuid: str):
        await self.db.retry(_uuid)

    async def cleanup(self):
        await self.db.cleanup()

    async def retry_processed_tasks(self):
        await self.db.retry_processed()

    async def cancel(self, _uuid: str) -> bool:
        for running_task in self.view_running_tasks():
            if _uuid == running_task[0].submitted_task.uuid:
                try:
                    running_task[1].terminate()
                except ProcessLookupError:
                    pass
                except Exception as e:
                    raise e
        for queued_task in await self.db.list_all():
            if _uuid == queued_task.submitted_task.uuid:
                await self.db.cancel(queued_task.submitted_task.uuid)
                return True
        return False

    @staticmethod
    def calc_next_wait(wait: float) -> float:
        jitter = random()
        return min(5, wait + jitter)

    @staticmethod
    async def wait_for_process_status(_id: int, process: Union[TaskProcessorException, Process]) -> TaskStatus:
        logger.info("Worker id: {} - Waiting for process".format(_id))
        if isinstance(process, Process):
            logger.info("Worker id: {} - Waiting on task".format(_id))
            return_code = await process.wait()
            logger.info("Worker id: {} - Return code: {}".format(_id, return_code))

            if return_code == 0:
                return TaskStatus.DONE
            else:
                return TaskStatus.FAILED
        else:
            logger.warn("Worker id: {} - Process failure: {}".format(_id, process.message))
            return TaskStatus.FAILED

    async def _worker(self, _id: int, init_wait: float, db: SQLiteDatasource):
        wait_time = init_wait

        while True:
            wait_time = self.calc_next_wait(wait_time)
            logger.debug("Worker id: {} - Waiting for {}".format(_id, wait_time))
            await sleep(wait_time)

            # Locking reduces transaction deadlocks in sqlite to zero
            # Pulling one task a time from the queue is acceptable behavior to me
            async with self._lock:
                logger.debug("Worker id: {} - Getting task".format(_id))
                task: Optional[DownloadTask] = await db.get()

            if task is not None:
                logger.info("Worker id: {} - Downloading {}".format(_id, task.submitted_task.url))

                process: Union[TaskProcessorException, Process] = await self.task_processor.process(task)

                if isinstance(process, Process):
                    self._running_tasks[_id] = (task, process)
                    status = await self.wait_for_process_status(_id, process)
                    del (self._running_tasks[_id])
                else:
                    status = await self.wait_for_process_status(_id, process)

                await db.set_status(task.submitted_task.uuid, status)
                wait_time = init_wait
