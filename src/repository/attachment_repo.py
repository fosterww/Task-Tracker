from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import (
    AppError,
    AttachmentNotFoundError,
    DatabaseIntegrityError,
)
from src.core.logger import logger
from src.models.task import TaskAttachments, TaskModel


class SQLAlachemyAttachmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_task(self, user_id: int, task_id: int) -> list[TaskAttachments]:
        try:
            query = (
                select(TaskAttachments)
                .join(TaskModel)
                .where(
                    TaskAttachments.task_id == task_id, TaskModel.author_id == user_id
                )
            )
            result = await self.session.execute(query)
            attachments = result.scalars().all()

            if attachments is None:
                raise AttachmentNotFoundError()

            return list(attachments)
        except SQLAlchemyError as e:
            logger.error(
                f"Error with getting attachments by task_id for user {user_id}: {e}"
            )
            raise AppError("Cannot list all tasks")

    async def get_by_id(
        self, user_id: int, attachment_id: int
    ) -> TaskAttachments | None:
        try:
            query = (
                select(TaskAttachments)
                .join(TaskModel)
                .where(
                    TaskAttachments.id == attachment_id, TaskModel.author_id == user_id
                )
            )
            result = await self.session.execute(query)
            attachment = result.scalar_one_or_none()

            if attachment is None:
                raise AttachmentNotFoundError()
            return attachment
        except SQLAlchemyError as e:
            logger.error(f"Error with getting by attachment id for user {user_id}: {e}")
            raise AppError("Cannot list all tasks")

    async def delete(self, attachment: TaskAttachments) -> None:
        try:
            await self.session.delete(attachment)
            await self.session.commit()
        except SQLAlchemyError as e:
            logger.error(f"Error with deleting attachment {attachment.id}: {e}")
            raise AppError("Cannot list all tasks")

    async def create(
        self, task_id: int, filename: str, s3_key: str, size: int, content_type: str
    ) -> TaskAttachments:
        try:
            new_attachment = TaskAttachments(
                filename=filename,
                s3_key=s3_key,
                size=size,
                content_type=content_type,
                task_id=task_id,
            )
            self.session.add(new_attachment)
            await self.session.commit()
            await self.session.refresh(new_attachment)
            return new_attachment
        except IntegrityError as e:
            await self.session.rollback()
            logger.warning(f"Integrity error: {e}")
            raise DatabaseIntegrityError("Data constraints violated")
        except SQLAlchemyError as e:
            logger.error(f"Error with creating attachment: {e}")
            raise AppError("Cannot list all tasks")
