from typing import List

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AppError, DatabaseIntegrityError
from src.core.logger import logger
from src.models.category import CategoryModel
from src.schemas.category import CategoryCreate


class SQLAlchemyCategoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self, user_id: int) -> List[CategoryModel]:
        try:
            query = select(CategoryModel).where(CategoryModel.owner_id == user_id)
            result = await self.session.execute(query)
            categories = result.scalars().all()

            return categories

        except SQLAlchemyError as e:
            logger.error(f"Error with getting all tasks for user {user_id}: {e}")
            raise AppError("Cannot list all tasks")

    async def create(self, user_id: int, category_data: CategoryCreate) -> CategoryModel:
        try:
            data = category_data.model_dump(exclude_unset=True)
            new_category = CategoryModel(**data, owner_id=user_id)
            self.session.add(new_category)
            await self.session.commit()
            await self.session.refresh(new_category)
            return new_category
        except IntegrityError as e:
            await self.session.rollback()
            logger.warning(f"Integrity error for user {user_id}: {e}")
            raise DatabaseIntegrityError("Invalid category_id or data constraints violated")
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Unexpected DB error: {e}")
            raise AppError("Internal database error")
