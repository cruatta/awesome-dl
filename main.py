from awesomedl.model import *
from awesomedl.backend.ytdl import YTDL
from fastapi import FastAPI
from typing import *

app = FastAPI()
ytdl = YTDL()


@app.post("/ytdl/task")
async def add_task(task: DownloadRequest) -> SubmittedTask:
    task = await ytdl.add(task)
    return task


@app.get("/ytdl/task")
def get_tasks() -> Any:
    return ytdl.tasks()


@app.get("/ytdl/task/stdout/{uuid}")
async def get_stdout(uuid: str) -> Any:
    return await ytdl.stdout(uuid)


@app.get("/ytdl/task/running")
async def get_running_tasks() -> Any:
    return await ytdl.running()


@app.post("/ytdl/task/cancel")
def cancel_task(pid: PID) -> Any:
    return {"success": ytdl.cancel(pid)}

