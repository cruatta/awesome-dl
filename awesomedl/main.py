import os
from typing import *

from awesomedl.backend.root import RootBackend
from awesomedl.backend.ytdl import YTDLBackend
from awesomedl.config import ConfigManager
from awesomedl.datasource.sqlite import SQLiteDatasource
from awesomedl.model import *
from awesomedl.queue import TaskQueue
from awesomedl.process.task_processor import TaskProcessor
from awesomedl.util import make_check_authorization_header
from awesomedl.vars import *
from fastapi import Depends, FastAPI
from fastapi.logger import logger
from fastapi.security import APIKeyHeader

X_ADL_KEY = APIKeyHeader(name=API_KEY_HEADER)
adl_key_hashed = os.environ.get(ADL_KEY)

config = ConfigManager.config_path()

if config is None:
    logger.warning("Starting up without configuration")

config_manager = ConfigManager(config)
task_processor = TaskProcessor(config_manager)
db = SQLiteDatasource('sqlite:///awesome.db')
app = FastAPI(title="Awesome-dl",
              description="An awesome download manager",
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


@app.get("/ytdl/profiles", response_model=List[str], dependencies=[Depends(check_authorization_header)])
def get_ytdl_profiles() -> List[str]:
    return config_manager.list(TaskType.YTDL)


@app.get("/task/all", response_model=List[SubmittedTaskModel], dependencies=[Depends(check_authorization_header)])
async def get_tasks() -> List[SubmittedTaskModel]:
    return await root.all()


@app.get("/task/running", response_model=List[SubmittedTaskModel], dependencies=[Depends(check_authorization_header)])
async def get_task_running() -> List[SubmittedTaskModel]:
    return await root.running()


@app.get("/task/progress/{uuid}", response_model=List[TaskProgressModel], dependencies=[Depends(check_authorization_header)])
async def get_task_progress(uuid: str) -> List[TaskProgressModel]:
    return await root.progress(UUIDModel(uuid=uuid))


@app.post("/task/cleanup", response_model=ResultModel, dependencies=[Depends(check_authorization_header)])
async def cleanup_tasks() -> ResultModel:
    await root.cleanup()
    return ResultModel.create(ok=True)


@app.post("/task/cancel", response_model=ResultModel, dependencies=[Depends(check_authorization_header)])
async def cancel_task(uuid: UUIDModel) -> ResultModel:
    result = await root.cancel(uuid)
    return ResultModel.create(ok=result)


@app.post("/task/retry/processed", response_model=ResultModel, dependencies=[Depends(check_authorization_header)])
async def retry_processed_tasks() -> ResultModel:
    await root.retry_processed_tasks()
    return ResultModel.create(ok=True)


@app.post("/task/retry", response_model=ResultModel, dependencies=[Depends(check_authorization_header)])
async def retry_task(uuid: UUIDModel) -> ResultModel:
    await root.retry_task(uuid)
    return ResultModel.create(ok=True)


@app.get("/health", response_model=HealthModel, dependencies=[Depends(check_authorization_header)])
def get_health() -> HealthModel:
    return HealthModel.create('Awesome-dl', VERSION)
