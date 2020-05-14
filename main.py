from awesomedl.model import *
from awesomedl.backend.ytdl import YTDL
from fastapi import FastAPI
from typing import *

app = FastAPI()
ytdl = YTDL()


@app.post("/task")
async def add_task(task: DownloadRequest) -> SubmittedTask:
    task = await ytdl.add(task)
    return task


@app.get("/task")
def get_tasks() -> Any:
    return {"tasks": ytdl.tasks()}


@app.get("/task/stdout/{uuid}")
async def get_tasks(uuid: str) -> Any:
    return await ytdl.stdout(uuid)


@app.get("/task/running")
def get_running_tasks() -> Any:
    return {"running": ytdl.running()}


@app.post("/task/cancel")
def cancel_task(pid: PID) -> Any:
    return {"success": ytdl.cancel(pid)}

