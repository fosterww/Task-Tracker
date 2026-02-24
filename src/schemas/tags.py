from pydantic import BaseModel, ConfigDict


class TaskTagBase(BaseModel):
    name: str
    color: str | None = None


class TaskTagCreate(TaskTagBase):
    pass


class TaskTagResponse(TaskTagBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
