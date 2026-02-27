from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AppError, DatabaseIntegrityError, TaskNotFoundError
from src.core.logger import logger
from src.models.task import TaskModel, TaskPriority, TaskStatus, TaskTagModel
from src.schemas.task import TaskBase, TaskCreate


class SQLAlchemyTaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(
        self,
        user_id: int,
        status: Optional[TaskStatus] = None,
        category_id: Optional[int] = None,
        priority: Optional[TaskPriority] = None,
    ) -> List[TaskModel]:
        try:
            query = select(TaskModel).where(TaskModel.author_id == user_id)

            if status:
                query = query.where(TaskModel.status == status)
            if category_id:
                query = query.where(TaskModel.category_id == category_id)
            if priority:
                query = query.where(TaskModel.priority == priority)

            query = query.order_by(
                TaskModel.priority.desc(), TaskModel.deadline.asc().nullslast()
            )

            result = await self.session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error with getting all tasks for user {user_id}: {e}")
            raise AppError("Cannot list all tasks")

    async def create(
        self, user_id: int, task_data: TaskCreate, tags: list[TaskTagModel] = None
    ) -> TaskModel:
        try:
            data = task_data.model_dump(exclude_unset=True)
            data.pop("tags", None)
            new_task = TaskModel(**data, author_id=user_id)
            if tags:
                new_task.tags = tags
            self.session.add(new_task)
            await self.session.commit()

            query = select(TaskModel).where(TaskModel.id == new_task.id)
            result = await self.session.execute(query)
            return result.scalar_one()

        except IntegrityError as e:
            await self.session.rollback()
            logger.warning(f"Integrity error for user {user_id}: {e}")
            raise DatabaseIntegrityError(
                "Invalid category_id or data constraints violated"
            )
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Unexpected DB error: {e}")
            raise AppError("Internal database error")

    async def get_by_id(self, task_id: int, user_id: int) -> Optional[TaskModel]:
        try:
            query = select(TaskModel).where(
                TaskModel.id == task_id, TaskModel.author_id == user_id
            )
            result = await self.session.execute(query)
            task = result.scalar_one_or_none()

            if task is None:
                raise TaskNotFoundError()

            return task
        except SQLAlchemyError as e:
            logger.error(f"Error while getting task {task_id}: {e}")
            raise AppError("Error while getting task from db")

    async def update(
        self, task_id: int, user_id: int, task_data: TaskBase
    ) -> TaskModel:
        task = await self.get_by_id(task_id, user_id)
        if not task:
            raise TaskNotFoundError()
        try:
            data = task_data.model_dump(exclude_unset=True)
            for key, value in data.items():
                setattr(task, key, value)

            await self.session.commit()

            query = select(TaskModel).where(TaskModel.id == task_id)
            result = await self.session.execute(query)
            return result.scalar_one()

        except IntegrityError as e:
            await self.session.rollback()
            logger.warning(f"Error while updating task {task_id}: {e}")
            raise DatabaseIntegrityError("Invalid data for update")
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"DB Error while updating task {task_id}: {e}")
            raise AppError("Failed to update task")

    async def delete(self, task_id: int, user_id: int) -> None:
        try:
            query = select(TaskModel).where(
                TaskModel.author_id == user_id, TaskModel.id == task_id
            )
            result = await self.session.execute(query)
            task = result.scalar_one_or_none()

            if task is None:
                raise TaskNotFoundError()

            await self.session.delete(task)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Unexpected DB error: {e}")
            raise AppError("Internal database error")
