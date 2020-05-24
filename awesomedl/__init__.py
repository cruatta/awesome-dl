import os
from pathlib import Path
from typing import *

from awesomedl.backend.root import RootBackend
from awesomedl.backend.ytdl import YTDLBackend
from awesomedl.config import ConfigManager
from awesomedl.datasource.sqlite import SQLiteDatasource
from awesomedl.model import TaskType
from awesomedl.model.views import *
from awesomedl.queue import TaskQueue
from awesomedl.util import make_check_authorization_header
from awesomedl.vars import *
from fastapi import Depends, FastAPI
from fastapi.logger import logger
from fastapi.security import APIKeyHeader

X_ADL_KEY = APIKeyHeader(name=API_KEY_HEADER)
adl_key_hashed = os.environ.get(ADL_KEY)

ytdl_config_path: str = os.environ.get(YTDL_CONFIG_PATH) or str(Path(Path.home(), ".config", "awesome", "ytdl"))

config_manager = ConfigManager(Path(ytdl_config_path))
db = SQLiteDatasource()
app = FastAPI(title="awesome-dl",
              description="A download manager for Youtube-DL and beyond",
              version=VERSION)
task_queue = TaskQueue(db, config_manager)
ytdl = YTDLBackend(task_queue)
root = RootBackend(task_queue)


if not adl_key_hashed:
    logger.warning("Missing {} environment variable. API key protection is disabled".format(ADL_KEY))

check_authorization_header = make_check_authorization_header(adl_key_hashed, X_ADL_KEY)


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


@app.get("/ytdl/formats", dependencies=[Depends(check_authorization_header)])
def get_ytdl_formats() -> List[str]:
    return config_manager.list(TaskType.YTDL)


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
    await root.cleanup()
    return {"success": True}


@app.post("/task/cancel", dependencies=[Depends(check_authorization_header)])
async def cancel_task(uuid: UUIDModel) -> Any:
    return {"success": await root.cancel(uuid)}


@app.post("/task/retry/processed", dependencies=[Depends(check_authorization_header)])
async def retry_processed_tasks() -> Any:
    await root.retry_processed_tasks()
    return {"success": True}


@app.post("/task/retry", dependencies=[Depends(check_authorization_header)])
async def retry_task(uuid: UUIDModel) -> Any:
    await root.retry_task(uuid)
    return {"success": True}
