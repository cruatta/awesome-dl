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
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

X_ADL_KEY = APIKeyHeader(name=API_KEY_HEADER)
adl_key_hashed = os.environ.get(ADL_KEY)
dev_mode = os.environ.get("DEV_MODE") and os.environ.get("DEV_MODE").lower() in ['true', '1', 'yes', 'y']

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

# TODO Add check for dev env
if dev_mode: 
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.on_event("startup")
async def startup():
    await db.connect()
    await db.initialize()


@app.on_event("shutdown")
async def shutdown():
    await task_queue.kill_workers()
    await db.disconnect()


app.mount("/ui", StaticFiles(directory="frontend/build", html=True), name="ui")


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


@app.get("/task/progress/{uuid}", response_model=List[ProgressModel], dependencies=[Depends(check_authorization_header)])
async def get_task_progress(uuid: str) -> List[ProgressModel]:
    return await root.progress(UUIDModel(uuid=uuid))


@app.post("/task/cleanup", response_model=ResultModel, dependencies=[Depends(check_authorization_header)])
async def cleanup_tasks() -> ResultModel:
    return await root.cleanup()


@app.post("/task/cancel", response_model=List[CancelModel], dependencies=[Depends(check_authorization_header)])
async def cancel_task(uuid: UUIDModel) -> List[CancelModel]:
    return await root.cancel(uuid)


@app.post("/task/cancel/all", response_model=List[CancelModel], dependencies=[Depends(check_authorization_header)])
async def cancel_all_tasks() -> List[CancelModel]:
    return await root.cancel_all()


@app.post("/task/retry/processed", response_model=ResultModel, dependencies=[Depends(check_authorization_header)])
async def retry_processed_tasks() -> ResultModel:
    return await root.retry_processed_tasks()


@app.post("/task/retry", response_model=ResultModel, dependencies=[Depends(check_authorization_header)])
async def retry_task(uuid: UUIDModel) -> ResultModel:
    return await root.retry_task(uuid)


@app.get("/health", response_model=HealthModel, dependencies=[Depends(check_authorization_header)])
def get_health() -> HealthModel:
    return HealthModel.create('Awesome-dl', VERSION)
