from enum import Enum


class Status(Enum):
    NONE = None
    CREATED = "created"
    PROCESS = "process"
    REJECTED = "rejected"
    DONE = "done"
