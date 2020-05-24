from enum import IntEnum, Enum, unique


@unique
class TaskStatus(IntEnum):
    CREATED = 0
    PROCESSING = 1
    CANCELLED = 2
    DONE = 3
    FAILED = 4


@unique
class TaskType(Enum):
    YTDL = "ytdl"