from awesomedl.model.__init__ import SubmittedTaskModel, DownloadTask, YTDLDownloadTask, TaskStatus, TaskType
from databases import Database

from typing import *


class SQLiteDatasource(object):

    create_tbl_sub_tasks = """
        CREATE TABLE IF NOT EXISTS Tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uuid VARCHAR(100) NOT NULL UNIQUE,
            type VARCHAR(100) NOT NULL,
            url VARCHAR(1000),
            status INTEGER,
            profile VARCHAR(1000),
            submitted_ts VARCHAR(100)
        )
    """

    def __init__(self, db_path: str):
        self.database = Database(db_path)

    @staticmethod
    def _row_to_download_task(row: Optional[Mapping]) -> Optional[DownloadTask]:
        if row is not None:
            uuid = row["uuid"]
            url = row["url"]
            task_type = row["type"]
            profile = row["profile"]
            submitted_ts = row["submitted_ts"]
            status = TaskStatus(row["status"])

            submitted_task = SubmittedTaskModel.create(url, uuid, submitted_ts, status, profile)

            if task_type == repr(TaskType.YTDL):
                return YTDLDownloadTask(submitted_task)
            else:
                return None
        else:
            return None

    async def connect(self):
        await self.database.connect()

    async def initialize(self):
        await self.database.execute(query=self.create_tbl_sub_tasks)

    async def disconnect(self):
        await self.database.disconnect()

    async def put(self, task: DownloadTask):
        task_type = repr(task.type)
        query = """
            INSERT INTO Tasks(uuid, type, url, profile, submitted_ts, status) 
            VALUES (:uuid, :type, :url, :profile, :submitted_ts, :status)
        """

        params = {
            "uuid": task.submitted_task.uuid,
            "type": task_type,
            "url": task.submitted_task.url,
            "submitted_ts": task.submitted_task.submitted_ts,
            "profile": task.submitted_task.profile,
            "status": task.submitted_task.status
        }
        await self.database.execute(query, params)

    async def get(self) -> Optional[DownloadTask]:
        select_query = """
        SELECT * FROM Tasks WHERE status = {} ORDER BY id ASC LIMIT 1 
        """.format(TaskStatus.Created)

        update_query = """
        UPDATE Tasks SET status = {} WHERE id = :id
        """.format(TaskStatus.Processing)

        async with self.database.transaction():
            row = await self.database.fetch_one(select_query, None)
            if row is not None:
                param = {
                    "id": row["id"]
                }
                await self.database.execute(update_query, param)
                task = self._row_to_download_task(row)
                if task is not None:
                    task.submitted_task.status = TaskStatus.Processing
                return task
            else:
                return None

    async def retry_processed(self):
        update_query = """
        UPDATE Tasks SET status = {} WHERE status = {}
        """.format(TaskStatus.Created, TaskStatus.Processing)

        await self.database.execute(update_query, None)

    async def retry(self, _uuid: str):
        update_query = """
        UPDATE Tasks SET status = {} WHERE uuid = :uuid
        """.format(TaskStatus.Created)

        params = {
            "uuid": _uuid
        }

        await self.database.execute(update_query, params)

    async def cleanup(self):
        delete_query = """
        DELETE FROM Tasks WHERE status IN ({}, {}, {})
        """.format(TaskStatus.Done, TaskStatus.Cancelled, TaskStatus.Failed)

        await self.database.execute(delete_query, None)

    async def set_status(self, uuid: str, status: TaskStatus):
        update_query = """
        UPDATE Tasks SET status = :status WHERE uuid = :uuid
        """

        params = {
            "status": status,
            "uuid": uuid
        }
        await self.database.execute(update_query, params)

    async def cancel(self, uuid: str):
        update_query = """
        UPDATE Tasks SET status = {} WHERE uuid = :uuid
        """.format(TaskStatus.Cancelled)

        params = {
            "uuid": uuid
        }
        await self.database.execute(update_query, params)

    async def get_by_uuid(self, uuid: str) -> Optional[DownloadTask]:
        param = {
            "uuid": uuid
        }

        query = """
        SELECT * FROM Tasks WHERE uuid = :uuid
        """

        row = await self.database.fetch_one(query, param)
        return self._row_to_download_task(row)

    async def _list_by(self, query) -> List[DownloadTask]:
        list_rows = await self.database.fetch_all(query, None)
        maybe_tasks: Iterator[Optional[DownloadTask]] = map(self._row_to_download_task, list_rows)
        return [task for task in maybe_tasks if task is not None]

    async def list_all(self) -> List[DownloadTask]:
        query = "SELECT * FROM Tasks"
        return await self._list_by(query)

    async def list_running(self) -> List[DownloadTask]:
        query = "SELECT * FROM Tasks WHERE status = {}".format(TaskStatus.Processing)
        return await self._list_by(query)

    async def list_queued(self) -> List[DownloadTask]:
        query = "SELECT * FROM Tasks WHERE status = {}".format(TaskStatus.Created)
        return await self._list_by(query)
