from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AppError
from src.core.logger import logger
from src.models.task import TaskTagModel


class SQLAlchemyTaskTagRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_or_get(self, tag_names: list[str]) -> list[TaskTagModel]:
        if not tag_names:
            return []
        try:
            query = select(TaskTagModel).where(TaskTagModel.name.in_(tag_names))
            result = await self.session.execute(query)
            existing_tags = list(result.scalars().all())
            existing_names = [t.name for t in existing_tags]

            new_tags = [
                TaskTagModel(name=name)
                for name in tag_names
                if name not in existing_names
            ]

            if new_tags:
                self.session.add_all(new_tags)
                await self.session.flush()

            return existing_tags + new_tags
        except SQLAlchemyError as e:
            logger.error(f"Error in get_or_create_tags: {e}")
            raise AppError("Failed to process tags")
