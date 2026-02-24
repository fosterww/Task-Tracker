from collections.abc import AsyncGenerator
from typing import Any

from dishka import Provider, Scope, from_context, provide
from fastapi import HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.config import settings
from src.models.user import UserModel
from src.repository.base import (
    ICategoryRepository,
    ISubTaskRepository,
    ITaskRepository,
    ITaskTagRepository,
    ITokenRepository,
    IUserRepository,
)
from src.repository.category_repo import SQLAlchemyCategoryRepository
from src.repository.subtask_repo import SQLAlchemySubTaskRepository
from src.repository.tag_repo import SQLAlchemyTaskTagRepository
from src.repository.task_repo import SQLAlchemyTaskRepository
from src.repository.user_repo import SQLAlchemyTokenRepository, SQLAlchemyUserRepository
from src.services.task import TaskService


class AppProvider(Provider):
    request = from_context(provides=Request, scope=Scope.REQUEST)

    @provide(scope=Scope.APP)
    def get_engine(self) -> AsyncEngine:
        return create_async_engine(settings.DATABASE_URL)

    @provide(scope=Scope.APP)
    def get_sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker:
        return async_sessionmaker(bind=engine, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def get_db(
        self, sessionmaker: async_sessionmaker
    ) -> AsyncGenerator[AsyncSession, Any]:
        async with sessionmaker() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def get_task_repo(self, session: AsyncSession) -> ITaskRepository:
        return SQLAlchemyTaskRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_user_repo(self, session: AsyncSession) -> IUserRepository:
        return SQLAlchemyUserRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_token_repo(self, session: AsyncSession) -> ITokenRepository:
        return SQLAlchemyTokenRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_category_repo(self, session: AsyncSession) -> ICategoryRepository:
        return SQLAlchemyCategoryRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_subtask_repo(self, session: AsyncSession) -> ISubTaskRepository:
        return SQLAlchemySubTaskRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_tag_repo(self, session: AsyncSession) -> ITaskTagRepository:
        return SQLAlchemyTaskTagRepository(session)

    @provide(scope=Scope.REQUEST)
    def get_task_service(
        self, task_repo: ITaskRepository, tag_repo: ITaskTagRepository
    ) -> TaskService:
        return TaskService(task_repo, tag_repo)

    @provide(scope=Scope.REQUEST)
    async def get_current_user(
        self, request: Request, user_repo: IUserRepository
    ) -> UserModel:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
            )
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            id = payload.get("sub")
            if id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )
            user_id = int(id)
        except (JWTError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        user = await user_repo.get_by_id(user_id)

        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user
