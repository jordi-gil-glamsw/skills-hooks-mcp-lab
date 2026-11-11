from enum import StrEnum

from pydantic import BaseModel, Field


class TaskStatus(StrEnum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    description: str | None = None


class Task(TaskCreate):
    id: int
    status: TaskStatus = TaskStatus.todo
