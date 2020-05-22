from awesomedl.model.views import *
from awesomedl.queue import TaskQueue
from awesomedl.backend.ytdl import YTDLBackend
from awesomedl.backend.root import RootBackend
from awesomedl.depends import check_authorization_header
from fastapi import FastAPI
from typing import *
from fastapi import Depends
from awesomedl.datasource.sqlite import SQLiteDatasource

db = SQLiteDatasource()
app = FastAPI()
task_queue = TaskQueue(db)
ytdl = YTDLBackend(task_queue)
root = RootBackend(task_queue)


@app.on_event("startup")
async def startup():
    await db.connect()
    await db.initialize()


@app.on_event("shutdown")
async def shutdown():
    await task_queue.kill_workers()
    await db.database.disconnect()


@app.post("/ytdl/task", dependencies=[Depends(check_authorization_header)])
async def add_task(task: DownloadRequestModel) -> SubmittedTaskModel:
    return await ytdl.add(task)


@app.get("/task/queue", dependencies=[Depends(check_authorization_header)])
async def get_queued_tasks() -> Any:
    return await root.queued()


@app.get("/task/stdout/{uuid}", dependencies=[Depends(check_authorization_header)])
async def get_stdout(uuid: str) -> Any:
    return await root.stdout(uuid)


@app.get("/task/running", dependencies=[Depends(check_authorization_header)])
async def get_running_tasks() -> Any:
    return await root.running()


@app.post("/task/cleanup", dependencies=[Depends(check_authorization_header)])
async def cleanup_tasks() -> Any:
    return await root.cleanup()


@app.post("/task/cancel", dependencies=[Depends(check_authorization_header)])
async def cancel_task(pid: UUIDModel) -> Any:
    return {"success": await root.cancel(pid)}


@app.post("/task/retry/all", dependencies=[Depends(check_authorization_header)])
async def cancel_task() -> Any:
    return await db.retry_all()
