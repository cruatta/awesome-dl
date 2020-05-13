from awesomedl import DownloadTask
from awesomedl.client.ytdl import *
from fastapi import FastAPI
from typing import *

app = FastAPI()
ytdl = YTDL()


@app.post("/")
def add_task(task: DownloadTask) -> Any:
    ytdl.add(task)
    return "ok"


@app.get("/")
async def get_tasks() -> Any:
    return {"success": True, "dl_queue": ytdl.tasks()}



