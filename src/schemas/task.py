from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, field_validator

from src.models.task import TaskPriority, TaskStatus
from src.schemas.category import CategoryResponse
from src.schemas.tags import TaskTagResponse


class TaskBase(BaseModel):
    title: str
    description: str | None = None
    deadline: datetime | None = None
    category_id: int | None = None
    status: TaskStatus | None = TaskStatus.NOTSTARTED
    priority: TaskPriority | None = TaskPriority.LOW


class TaskCreate(TaskBase):
    tags: list[str] = []

    @field_validator("deadline")
    @classmethod
    def deadline_must_be_future(cls, v: datetime | None) -> datetime | None:
        if v:
            now = datetime.now(timezone.utc)
            if v.tzinfo is None:
                if v < now.replace(tzinfo=None):
                    raise ValueError("Deadline cannot be in the past")
            else:
                if v < now:
                    raise ValueError("Deadline cannot be in the past")
        return v


class SubTaskBase(BaseModel):
    title: str
    is_done: bool = False


class SubTaskCreate(SubTaskBase):
    pass


class SubTaskResponse(SubTaskBase):
    id: int
    parent_task_id: int

    model_config = ConfigDict(from_attributes=True)


class TaskResponse(TaskBase):
    id: int
    status: TaskStatus = TaskStatus.NOTSTARTED
    priority: TaskPriority = TaskPriority.LOW
    author_id: int
    subtasks: list[SubTaskResponse] = []
    category: CategoryResponse | None = None
    tags: list[TaskTagResponse] = []

    model_config = ConfigDict(from_attributes=True)
