from awesomedl.model import *
from awesomedl.task.queue import TaskQueue
from awesomedl.backend.ytdl import YTDL
from awesomedl.backend import BaseBackend
from fastapi import FastAPI
from typing import *

app = FastAPI()
task_queue = TaskQueue()
ytdl = YTDL(task_queue)
base = BaseBackend(task_queue)


@app.post("/ytdl/task")
async def add_task(task: DownloadRequestModel) -> SubmittedTaskModel:
    return await ytdl.add(task)


@app.get("/task/queue")
def get_task_queue() -> Any:
    return base.tasks()


@app.get("/task/stdout/{uuid}")
async def get_stdout(uuid: str) -> Any:
    return await base.stdout(uuid)


@app.get("/task/running")
async def get_running_tasks() -> Any:
    return await base.running()


@app.post("/task/cancel")
def cancel_task(pid: UUIDModel) -> Any:
    return {"success": base.cancel(pid)}

