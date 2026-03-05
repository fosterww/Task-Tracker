from typing import List, Optional

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request, status

from src.core.limiter import limiter
from src.models.task import TaskPriority, TaskStatus
from src.models.user import UserModel
from src.repository.base import ISubTaskRepository, ITaskRepository
from src.schemas.task import (
    SubTaskCreate,
    SubTaskResponse,
    TaskBase,
    TaskCreate,
    TaskResponse,
)
from src.services.task import TaskService

router = APIRouter(prefix="/tasks", tags=["tasks"], route_class=DishkaRoute)


@router.get("/")
@limiter.limit("5/minute")
async def get_tasks(
    request: Request,
    repo: FromDishka[ITaskRepository],
    current_user: FromDishka[UserModel],
    status: Optional[TaskStatus] = None,
    category_id: Optional[int] = None,
    priority: Optional[TaskPriority] = None,
) -> List[TaskResponse]:
    return await repo.get_all(current_user.id, status, category_id, priority)


@router.post("/create-task", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_task(
    request: Request,
    task_data: TaskCreate,
    service: FromDishka[TaskService],
    current_user: FromDishka[UserModel],
) -> TaskResponse:
    return await service.create_task(current_user.id, task_data)


@router.patch("/{task_id}")
@limiter.limit("5/minute")
async def update_task(
    request: Request,
    task_id: int,
    task_data: TaskBase,
    repo: FromDishka[ITaskRepository],
    current_user: FromDishka[UserModel],
) -> TaskResponse:
    return await repo.update(task_id, current_user.id, task_data)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
async def delete_task(
    request: Request,
    task_id: int,
    repo: FromDishka[ITaskRepository],
    current_user: FromDishka[UserModel],
) -> None:
    return await repo.delete(task_id, current_user.id)


@router.post("/{task_id}/subtasks")
@limiter.limit("5/minute")
async def create_subtask(
    request: Request,
    task_id: int,
    subtask_data: SubTaskCreate,
    repo: FromDishka[ISubTaskRepository],
    current_user: FromDishka[UserModel],
) -> SubTaskResponse:
    return await repo.create(current_user.id, task_id, subtask_data)


@router.patch("/subtasks/{subtask_id}/check")
@limiter.limit("5/minute")
async def check_subtask(
    request: Request,
    subtask_id: int,
    repo: FromDishka[ISubTaskRepository],
    current_user: FromDishka[UserModel],
) -> SubTaskResponse:
    return await repo.check(current_user.id, subtask_id)


@router.patch("/subtasks/{subtask_id}/uncheck")
@limiter.limit("5/minute")
async def uncheck_subtask(
    request: Request,
    subtask_id: int,
    repo: FromDishka[ISubTaskRepository],
    current_user: FromDishka[UserModel],
) -> SubTaskResponse:
    return await repo.uncheck(current_user.id, subtask_id)


@router.delete("/subtasks/{subtask_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
async def delete_subtask(
    request: Request,
    subtask_id: int,
    repo: FromDishka[ISubTaskRepository],
    current_user: FromDishka[UserModel],
) -> None:
    await repo.delete(current_user.id, subtask_id)
