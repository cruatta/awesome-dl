from awesomedl.model import *
from awesomedl.tasks.queue import TaskQueue
from awesomedl.backend.ytdl import YTDL
from fastapi import FastAPI
from typing import *

app = FastAPI()
task_queue = TaskQueue()
ytdl = YTDL(task_queue)


@app.post("/ytdl/task")
async def add_task(task: DownloadRequestModel) -> SubmittedTaskModel:
    return await ytdl.add(task)


@app.get("/task")
def get_tasks() -> Any:
    return ytdl.tasks()


@app.get("/task/stdout/{uuid}")
async def get_stdout(uuid: str) -> Any:
    return await ytdl.stdout(uuid)


@app.get("/task/running")
async def get_running_tasks() -> Any:
    return await ytdl.running()


@app.post("/task/cancel")
def cancel_task(pid: UUIDModel) -> Any:
    return {"success": ytdl.cancel(pid)}

