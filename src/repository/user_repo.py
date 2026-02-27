from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import AppError, UserAlreadyExistsError, UserNotFoundError
from src.core.logger import logger
from src.core.security import hash_password
from src.models.user import RefreshTokenModel, UserModel
from src.schemas.user import UserCreate


class SQLAlchemyUserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> Optional[UserModel]:
        try:
            query = select(UserModel).where(UserModel.id == user_id)
            result = await self.session.execute(query)
            user = result.scalar_one_or_none()

            if user is None:
                raise UserNotFoundError()

            return user

        except SQLAlchemyError as e:
            logger.error(f"Error getting user by id {user_id}: {e}")
            raise AppError("Database error while fetching user")

    async def get_by_email(self, email: str) -> Optional[UserModel]:
        try:
            query = select(UserModel).where(UserModel.email == email)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting user by email {email}: {e}")
            raise AppError("Database error while fetching user")

    async def create(self, user_data: UserCreate) -> UserModel:
        query = select(UserModel).where(UserModel.email == user_data.email)
        result = await self.session.execute(query)
        user = result.scalar_one_or_none()

        if user:
            raise UserAlreadyExistsError()

        try:
            hashed_pw = hash_password(user_data.password)
            username = user_data.email.split("@")[0]
            new_user = UserModel(
                username=username, email=user_data.email, hashed_password=hashed_pw
            )
            self.session.add(new_user)
            await self.session.commit()

            query = select(UserModel).where(UserModel.id == new_user.id)
            result = await self.session.execute(query)
            return result.scalar_one()
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error creating user {user_data.email}: {e}")
            raise AppError("Database error while creating user")


class SQLAlchemyTokenRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, token: str, user_id: int, expires_at: datetime) -> None:
        try:
            new_token = RefreshTokenModel(
                token=token, user_id=user_id, expires_at=expires_at
            )
            self.session.add(new_token)
            await self.session.commit()
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Error saving token for user {user_id}: {e}")
            raise AppError("Database error while saving token")

    async def get_by_token(self, token: str) -> Optional[RefreshTokenModel]:
        try:
            query = select(RefreshTokenModel).where(RefreshTokenModel.token == token)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching token: {e}")
            raise AppError("Database error while verifying token")
