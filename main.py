from awesomedl.model import *
from awesomedl.task.queue import TaskQueue
from awesomedl.backend.ytdl import YTDLBackend
from awesomedl.backend.root import RootBackend
from fastapi import FastAPI
from typing import *

app = FastAPI()
task_queue = TaskQueue()
ytdl = YTDLBackend(task_queue)
root = RootBackend(task_queue)


@app.post("/ytdl/task")
async def add_task(task: DownloadRequestModel) -> SubmittedTaskModel:
    return await ytdl.add(task)


@app.get("/task/queue")
def get_queued_tasks() -> Any:
    return root.queued()


@app.get("/task/stdout/{uuid}")
async def get_stdout(uuid: str) -> Any:
    return await root.stdout(uuid)


@app.get("/task/running")
async def get_running_tasks() -> Any:
    return await root.running()


@app.post("/task/cancel")
def cancel_task(pid: UUIDModel) -> Any:
    return {"success": root.cancel(pid)}

