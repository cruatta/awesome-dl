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
from awesomedl.process.task_processor import TaskProcessor
from awesomedl.util import make_check_authorization_header
from awesomedl.vars import *
from fastapi import Depends, FastAPI
from fastapi.logger import logger
from fastapi.security import APIKeyHeader

X_ADL_KEY = APIKeyHeader(name=API_KEY_HEADER)
adl_key_hashed = os.environ.get(ADL_KEY)

ytdl_config_path: str = os.environ.get(YTDL_CONFIG_PATH) or str(Path(Path.home(), ".config", "awesome", "ytdl"))

config_manager = ConfigManager(Path(ytdl_config_path))
task_processor = TaskProcessor(config_manager)
db = SQLiteDatasource('sqlite:///awesome.db')
app = FastAPI(title="awesome-dl",
              description="A download manager for Youtube-DL and beyond",
              version=VERSION)
task_queue = TaskQueue(db, task_processor)
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
    await db.disconnect()


@app.post("/ytdl/task", response_model=SubmittedTaskModel, dependencies=[Depends(check_authorization_header)])
async def add_task(task: DownloadRequestModel) -> SubmittedTaskModel:
    return await ytdl.add(task)


@app.get("/ytdl/formats", response_model=List[str], dependencies=[Depends(check_authorization_header)])
def get_ytdl_formats() -> List[str]:
    return config_manager.list(TaskType.YTDL)


@app.get("/task/queue", response_model=List[SubmittedTaskModel], dependencies=[Depends(check_authorization_header)])
async def get_queued_tasks() -> List[SubmittedTaskModel]:
    return await root.queued()


@app.get("/task/stdout/{uuid}", response_model=List[StdoutModel], dependencies=[Depends(check_authorization_header)])
async def get_stdout(uuid: str) -> List[StdoutModel]:
    return await root.stdout(UUIDModel(uuid=uuid))


@app.get("/task/running", response_model=List[TaskProgressModel], dependencies=[Depends(check_authorization_header)])
async def get_running_tasks() -> List[TaskProgressModel]:
    return await root.running()


@app.post("/task/cleanup", response_model=Result, dependencies=[Depends(check_authorization_header)])
async def cleanup_tasks() -> Result:
    await root.cleanup()
    return Result.create(ok=True)


@app.post("/task/cancel", response_model=Result, dependencies=[Depends(check_authorization_header)])
async def cancel_task(uuid: UUIDModel) -> Result:
    result = await root.cancel(uuid)
    return Result.create(ok=result)


@app.post("/task/retry/processed", response_model=Result, dependencies=[Depends(check_authorization_header)])
async def retry_processed_tasks() -> Result:
    await root.retry_processed_tasks()
    return Result.create(ok=True)


@app.post("/task/retry", response_model=Result, dependencies=[Depends(check_authorization_header)])
async def retry_task(uuid: UUIDModel) -> Result:
    await root.retry_task(uuid)
    return Result.create(ok=True)
