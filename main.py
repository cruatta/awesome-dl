from awesomedl.model import *
from awesomedl.task.queue import TaskQueue
from awesomedl.backend.ytdl import YTDLBackend
from awesomedl.backend.root import RootBackend
from awesomedl.depends import check_authorization_header
from fastapi import FastAPI
from typing import *
from fastapi import Depends

app = FastAPI()
task_queue = TaskQueue()
ytdl = YTDLBackend(task_queue)
root = RootBackend(task_queue)


@app.post("/ytdl/task", dependencies=[Depends(check_authorization_header)])
async def add_task(task: DownloadRequestModel) -> SubmittedTaskModel:
    return await ytdl.add(task)


@app.get("/task/queue", dependencies=[Depends(check_authorization_header)])
def get_queued_tasks() -> Any:
    return root.queued()


@app.get("/task/stdout/{uuid}", dependencies=[Depends(check_authorization_header)])
async def get_stdout(uuid: str) -> Any:
    return await root.stdout(uuid)


@app.get("/task/running", dependencies=[Depends(check_authorization_header)])
async def get_running_tasks() -> Any:
    return await root.running()


@app.post("/task/cancel", dependencies=[Depends(check_authorization_header)])
def cancel_task(pid: UUIDModel) -> Any:
    return {"success": root.cancel(pid)}

