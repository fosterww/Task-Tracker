from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AppError, DatabaseIntegrityError, TaskNotFoundError
from src.core.logger import logger
from src.models.task import SubTaskModel, TaskModel
from src.schemas.task import SubTaskCreate


class SQLAlchemySubTaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: int, task_id: int, subtask_data: SubTaskCreate) -> SubTaskModel:
        try:
            query = select(TaskModel).where(TaskModel.author_id == user_id, TaskModel.id == task_id)
            result = await self.session.execute(query)
            task = result.scalar_one_or_none()

            if task is None:
                raise TaskNotFoundError()

            data = subtask_data.model_dump(exclude_unset=True)
            new_subtask = SubTaskModel(
                **data,
                parent_task_id=task_id
            )

            self.session.add(new_subtask)
            await self.session.commit()
            await self.session.refresh(new_subtask)
            return new_subtask

        except IntegrityError as e:
            await self.session.rollback()
            logger.warning(f"Integrity error for user {user_id}: {e}")
            raise DatabaseIntegrityError("Invalid task_id or data constraints violated")
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Unexpected DB error: {e}")
            raise AppError("Internal database error")

    async def _update_status(self, user_id: int, subtask_id: int, is_done: bool) -> SubTaskModel:
        try:
            query = (
                select(SubTaskModel)
                .join(TaskModel)
                .where(
                    SubTaskModel.id == subtask_id,
                    TaskModel.author_id == user_id
                )
            )
            result = await self.session.execute(query)
            subtask = result.scalar_one_or_none()

            if subtask is None:
                raise TaskNotFoundError()

            subtask.is_done = is_done
            await self.session.commit()
            await self.session.refresh(subtask)
            return subtask

        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Unexpected DB error: {e}")
            raise AppError("Internal database error")

    async def check(self, user_id: int, subtask_id: int) -> SubTaskModel:
        return await self._update_status(user_id, subtask_id, True)

    async def uncheck(self, user_id: int, subtask_id: int) -> SubTaskModel:
        return await self._update_status(user_id, subtask_id, False)

    async def delete(self, user_id: int, subtask_id: int) -> None:
        try:
            query = (
                select(SubTaskModel)
                .join(TaskModel)
                .where(
                    SubTaskModel.id == subtask_id,
                    TaskModel.author_id == user_id
                )
            )
            result = await self.session.execute(query)
            subtask = result.scalar_one_or_none()

            if subtask is None:
                raise TaskNotFoundError()

            await self.session.delete(subtask)
            await self.session.commit()

        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Unexpected DB error: {e}")
            raise AppError("Internal database error")
