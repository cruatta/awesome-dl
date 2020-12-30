from awesomedl.datasource.sqlite import SQLiteDatasource
from awesomedl.model import TaskType, TaskStatus
import pytest  # type: ignore
import aiofiles.os  # type: ignore
import uuid
import sqlite3
from awesomedl.model import YTDLDownloadTask
from awesomedl.model.__init__ import SubmittedTaskModel


class TempDatabase:
    def __init__(self):
        self.path: str = str(uuid.uuid4()) + ".db"
        self.uri = "sqlite:///" + self.path
        self.db = SQLiteDatasource(self.uri)

    async def __aenter__(self) -> SQLiteDatasource:
        await self.db.connect()
        await self.db.initialize()
        return self.db

    async def __aexit__(self, exc_type, exc, tb):
        await self.db.disconnect()
        return await aiofiles.os.remove(self.path)


def make_task(url="whatever", uuid="whatever", submitted_ts="whatever", status=0, profile="audio") -> YTDLDownloadTask:
    s = SubmittedTaskModel.create(url, uuid, submitted_ts, status, profile)
    return YTDLDownloadTask(s)


@pytest.mark.asyncio
async def test_get_none():
    async with TempDatabase() as db:
        one = await db.get()
        assert one is None


@pytest.mark.asyncio
async def test_put_invalid_constraints():
    async with TempDatabase() as db:
        await db.put(make_task(uuid="1"))
        try:
            await db.put(make_task(uuid="1"))
            assert False
        except sqlite3.IntegrityError:
            assert True


@pytest.mark.asyncio
async def test_put_get():
    async with TempDatabase() as db:
        await db.put(make_task(uuid="1"))
        await db.put(make_task(uuid="2"))
        await db.put(make_task(uuid="3"))
        for i in range(1, 4):
            res = await db.get()
            assert res.type == TaskType.YTDL
            assert res.submitted_task.uuid == str(i)
            assert res.submitted_task.profile == "audio"
            assert res.submitted_task.status == TaskStatus.Processing
            assert res.submitted_task.submitted_ts == "whatever"
            assert res.submitted_task.url == "whatever"


@pytest.mark.asyncio
async def test_get_one_is_none():
    async with TempDatabase() as db:
        await db.put(make_task())
        await db.get()
        one = await db.get()
        assert one is None


@pytest.mark.asyncio
async def test_list_all():
    async with TempDatabase() as db:
        t1 = make_task(uuid="1", status=TaskStatus.Cancelled)
        t2 = make_task(uuid="2", status=TaskStatus.Processing)
        t3 = make_task(uuid="3", status=TaskStatus.Failed)
        t4 = make_task(uuid="4", status=TaskStatus.Created)
        t5 = make_task(uuid="5", status=TaskStatus.Done)
        await db.put(t1)
        await db.put(t2)
        await db.put(t3)
        await db.put(t4)
        await db.put(t5)

        res = await db.list_all()
        assert t1 in res
        assert t2 in res
        assert t3 in res
        assert t4 in res
        assert t5 in res


@pytest.mark.asyncio
async def test_list_running():
    async with TempDatabase() as db:
        await db.put(make_task(uuid="1"))
        await db.put(make_task(uuid="2"))
        await db.put(make_task(uuid="3", status=TaskStatus.Processing))
        res = await db.list_running()
        assert make_task(uuid="3", status=TaskStatus.Processing) in res


@pytest.mark.asyncio
async def test_list_queued():
    async with TempDatabase() as db:
        await db.put(make_task(uuid="1"))
        await db.put(make_task(uuid="2"))
        await db.put(make_task(uuid="3", status=TaskStatus.Processing))
        res = await db.list_queued()
        assert make_task(uuid="1") in res
        assert make_task(uuid="2") in res


@pytest.mark.asyncio
async def test_cancel():
    async with TempDatabase() as db:
        await db.put(make_task(uuid="1"))
        await db.put(make_task(uuid="2"))
        await db.put(make_task(uuid="3", status=TaskStatus.Processing))
        await db.cancel("1")
        await db.cancel("3")
        res = await db.list_all()
        assert make_task(uuid="1", status=TaskStatus.Cancelled) in res
        assert make_task(uuid="3", status=TaskStatus.Cancelled) in res
        assert make_task(uuid="2", status=TaskStatus.Created) in res


@pytest.mark.asyncio
async def test_get_by_uuid():
    async with TempDatabase() as db:
        await db.put(make_task(uuid="1"))
        await db.put(make_task(uuid="2"))
        await db.put(make_task(uuid="3"))
        res = await db.get_by_uuid("3")
        assert res.submitted_task.uuid == "3"


@pytest.mark.asyncio
async def test_set_status():
    async with TempDatabase() as db:
        await db.put(make_task(uuid="1", status=TaskStatus.Done))
        init = await db.get_by_uuid("1")
        assert init.submitted_task.status == TaskStatus.Done
        await db.set_status("1", TaskStatus.Processing)
        res = await db.get_by_uuid("1")
        assert res.submitted_task.uuid == "1"
        assert res.submitted_task.status == TaskStatus.Processing


@pytest.mark.asyncio
async def test_retry():
    async with TempDatabase() as db:
        await db.put(make_task(uuid="1", status=TaskStatus.Cancelled))
        init = await db.get_by_uuid("1")
        assert init.submitted_task.status == TaskStatus.Cancelled
        await db.retry("1")
        res = await db.get_by_uuid("1")
        assert res.submitted_task.uuid == "1"
        assert res.submitted_task.status == TaskStatus.Created


@pytest.mark.asyncio
async def test_retry_processed():
    async with TempDatabase() as db:
        await db.put(make_task(uuid="1", status=TaskStatus.Processing))
        await db.put(make_task(uuid="2", status=TaskStatus.Done))

        one = await db.get_by_uuid("1")
        two = await db.get_by_uuid("2")
        assert one.submitted_task.status == TaskStatus.Processing
        assert two.submitted_task.status == TaskStatus.Done

        await db.retry_processed()

        one = await db.get_by_uuid("1")
        two = await db.get_by_uuid("2")
        assert one.submitted_task.uuid == "1"
        assert one.submitted_task.status == TaskStatus.Created
        assert two.submitted_task.uuid == "2"
        assert two.submitted_task.status == TaskStatus.Done

@pytest.mark.asyncio
async def test_cleanup():
    async with TempDatabase() as db:
        t1 = make_task(uuid="1", status=TaskStatus.Cancelled)
        t2 = make_task(uuid="2", status=TaskStatus.Processing)
        t3 = make_task(uuid="3", status=TaskStatus.Failed)
        t4 = make_task(uuid="4", status=TaskStatus.Created)
        t5 = make_task(uuid="5", status=TaskStatus.Done)
        tasks = [t1, t2, t3, t4, t5]
        for t in tasks:
            await db.put(t)

        init = await db.list_all()
        assert init == tasks

        await db.cleanup()

        res = await db.list_all()
        assert t1 not in res
        assert t2 in res
        assert t3 not in res
        assert t4 in res
        assert t5 not in res


