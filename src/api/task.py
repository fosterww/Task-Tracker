from typing import List, Optional

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

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
async def get_tasks(
    repo: FromDishka[ITaskRepository],
    current_user: FromDishka[UserModel],
    status: Optional[TaskStatus] = None,
    category_id: Optional[int] = None,
    priority: Optional[TaskPriority] = None,
) -> List[TaskResponse]:
    return await repo.get_all(current_user.id, status, category_id, priority)


@router.post("/create-task", status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreate,
    service: FromDishka[TaskService],
    current_user: FromDishka[UserModel],
) -> TaskResponse:
    return await service.create_task(current_user.id, task_data)


@router.patch("/{task_id}")
async def update_task(
    task_id: int,
    task_data: TaskBase,
    repo: FromDishka[ITaskRepository],
    current_user: FromDishka[UserModel],
) -> TaskResponse:
    return await repo.update(task_id, current_user.id, task_data)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int, repo: FromDishka[ITaskRepository], current_user: FromDishka[UserModel]
) -> None:
    return await repo.delete(task_id, current_user.id)


@router.post("/{task_id}/subtasks")
async def create_subtask(
    task_id: int,
    subtask_data: SubTaskCreate,
    repo: FromDishka[ISubTaskRepository],
    current_user: FromDishka[UserModel],
) -> SubTaskResponse:
    return await repo.create(current_user.id, task_id, subtask_data)


@router.patch("/subtasks/{subtask_id}/check")
async def check_subtask(
    subtask_id: int,
    repo: FromDishka[ISubTaskRepository],
    current_user: FromDishka[UserModel],
) -> SubTaskResponse:
    return await repo.check(current_user.id, subtask_id)


@router.patch("/subtasks/{subtask_id}/uncheck")
async def uncheck_subtask(
    subtask_id: int,
    repo: FromDishka[ISubTaskRepository],
    current_user: FromDishka[UserModel],
) -> SubTaskResponse:
    return await repo.uncheck(current_user.id, subtask_id)


@router.delete("/subtasks/{subtask_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subtask(
    subtask_id: int,
    repo: FromDishka[ISubTaskRepository],
    current_user: FromDishka[UserModel],
) -> None:
    await repo.delete(current_user.id, subtask_id)
