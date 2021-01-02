from asyncio import Lock, create_task, sleep, CancelledError, InvalidStateError
from asyncio.subprocess import Process
from asyncio.tasks import Task
from random import random
from typing import *

from awesomedl.process.output import progress_output_parser, get_next_stdout
from awesomedl.process.task_processor import TaskProcessorException

from awesomedl.process.task_processor import TaskProcessor
from awesomedl.datasource.sqlite import SQLiteDatasource
from awesomedl.model import TaskStatus, DownloadTask, ProgressModel, TaskProgress
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

    def _running_tasks_with_process(self) -> Iterator[Tuple[DownloadTask, Process]]:
        return iter([twp for twp in self._running_tasks.values() if not twp[1].returncode])

    @staticmethod
    def _map_uuid(d: DownloadTask) -> str:
        return d.submitted_task.uuid

    # NOTE: This is not perfect. Theoretically, a task can transition states
    # from Created to Processing while this is happening and miss the process.
    # I am choosing to accept this race condition.
    def _get_process_by_uuid(self, uuid: str) -> Optional[Process]:
        process_list: List[Process] = [twp[1] for twp in
                                       self._running_tasks_with_process()
                                       if
                                       self._map_uuid(twp[0]) == uuid]

        len_process_list = len(process_list)
        if len_process_list > 1:
            logger.error("Found {} running processes matching uuid, expected 1 or 0".format(len_process_list))
            return None
        else:
            return process_list[0] if len_process_list == 1 else None

    async def wait_for_cancellations(self, max_wait_time: int,
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
        logger.warn("Starting worker shutdown")
        async with self._lock:
            for _id, worker in enumerate(self._workers):
                task: Optional[Tuple[DownloadTask, Process]] = self._running_tasks.get(_id)
                if task is not None:
                    task[1].kill()
                worker.cancel()
                try:
                    if worker.exception():
                        logger.warn("Worker shutting down {} caught exception={}".format(_id, str(worker.exception())))
                except CancelledError:
                    pass
                except InvalidStateError:
                    pass

        return await self.wait_for_cancellations(10)

    def view_running_tasks(self) -> Iterator[DownloadTask]:
        return iter([task[0] for task in self._running_tasks_with_process()])

    async def view_task(self, _uuid: str) -> Optional[Tuple[DownloadTask, TaskProgress]]:
        maybe_task: Optional[DownloadTask] = await self.db.get_by_uuid(_uuid)
        if maybe_task and maybe_task.submitted_task.status == TaskStatus.Done:
            return maybe_task, TaskProgress.complete()
        elif maybe_task:
            maybe_process = [task[1] for task in self._running_tasks.values() if task[0].submitted_task.uuid == _uuid]
            if maybe_process:
                maybe_progress: Optional[TaskProgress] = progress_output_parser(
                    maybe_task, await get_next_stdout(maybe_process[0])
                )
            else:
                maybe_progress = None
            progress: TaskProgress = maybe_progress if maybe_progress else TaskProgress.na()
            return maybe_task, progress
        else:
            return None

    async def view_all(self) -> List[DownloadTask]:
        return await self.db.list_all()

    async def add(self, task: DownloadTask):
        await self.db.put(task)

    async def retry(self, _uuid: str):
        await self.db.retry(_uuid)

    async def cleanup(self):
        await self.db.cleanup()

    async def retry_processed_tasks(self):
        await self.db.retry_processed()

    async def cancel_all(self) -> Dict[str, bool]:
        tasks = await self.db.list_running_or_queued()

        results = dict()
        for task in tasks:
            result = await self.cancel(self._map_uuid(task))
            if result is not None:
                results.update({self._map_uuid(task): result})
        return results

    async def cancel(self, _uuid: str) -> Optional[bool]:
        task: Optional[DownloadTask] = await self.db.get_by_uuid(_uuid)
        if task:
            process: Optional[Process] = self._get_process_by_uuid(_uuid)
            if process:
                try:
                    process.terminate()
                    success = True
                except ProcessLookupError as e:
                    logger.warn("Unable to find task {} - {}".format(_uuid, str(e)))
                    success = True
                except Exception as e:
                    logger.error("Unable to terminate task {} - {}".format(_uuid, str(e)))
                    success = False

                if success:
                    await self.db.cancel(task.submitted_task.uuid)
                return success
            else:
                await self.db.cancel(task.submitted_task.uuid)
                return True
        return None

    @staticmethod
    def calc_next_wait(wait: float) -> float:
        jitter = random()
        return min(5.0, wait + jitter)

    @staticmethod
    async def wait_for_process_status(_id: int, process: Union[TaskProcessorException, Process]) -> TaskStatus:
        logger.info("Worker id: {} - Waiting for process".format(_id))
        if isinstance(process, Process):
            logger.info("Worker id: {} - Waiting on task".format(_id))
            return_code = await process.wait()
            logger.info("Worker id: {} - Return code: {}".format(_id, return_code))

            if return_code == 0:
                return TaskStatus.Done
            else:
                return TaskStatus.Failed
        else:
            logger.warn("Worker id: {} - Process failure: {}".format(_id, process.message))
            return TaskStatus.Failed

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
