from awesomedl.model import *
from awesomedl.backend.ytdl import YTDL
from fastapi import FastAPI
from typing import *

app = FastAPI()
ytdl = YTDL()


@app.post("/task")
def add_task(task: DownloadRequest) -> SubmittedTask:
    return ytdl.add(task)


@app.get("/task")
def get_tasks() -> Any:
    return {"tasks": ytdl.tasks()}


@app.get("/task/running")
def get_running_tasks() -> Any:
    return {"running": ytdl.running()}


@app.post("/task/cancel")
def cancel_task(pid: PID) -> Any:
    cancelled = ytdl.cancel(pid)
    return {"success": cancelled}

