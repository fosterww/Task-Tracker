from typing import AsyncIterable, Any, AsyncGenerator

import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)
from redis.asyncio import Redis

from dishka import Scope, make_async_container, provide
from httpx import ASGITransport, AsyncClient

from dishka import Provider

from src.core.providers.auth import AuthProvider
from src.core.providers.repository import RepositoryProvider
from src.core.limiter import limiter
from src.database import Base
from src.main import app
from src.repository.base import (
    IAttachmentRepository,
    ITaskRepository,
    ITaskTagRepository,
)
from src.services.attachment import AttachmentService
from src.services.cache import CacheService
from src.services.task import TaskService
from src.services.storage import StorageService

limiter.enabled = False


class TestDatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def get_engine(self) -> AsyncEngine:
        return create_async_engine(
            "sqlite+aiosqlite:///:memory:", connect_args={"check_same_thread": False}
        )

    @provide(scope=Scope.APP)
    def get_sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker:
        return async_sessionmaker(bind=engine, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def get_db(
        self, sessionmaker: async_sessionmaker
    ) -> AsyncGenerator[AsyncSession, Any]:
        async with sessionmaker() as session:
            yield session

    @provide(scope=Scope.APP)
    async def get_redis(self) -> Redis:
        mock_redis = AsyncMock(spec=Redis)
        return mock_redis


class TestServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_task_service(
        self, task_repo: ITaskRepository, tag_repo: ITaskTagRepository
    ) -> TaskService:
        return TaskService(task_repo, tag_repo)

    @provide(scope=Scope.APP)
    def get_storage_service(self) -> StorageService:
        mock_storage = AsyncMock(spec=StorageService)
        mock_storage.upload_file.return_value = "mock_key"
        mock_storage.get_file_url.return_value = "http://mock-url.com"
        mock_storage.delete_file.return_value = None
        mock_storage.ensure_bucket.return_value = None
        return mock_storage

    @provide(scope=Scope.APP)
    def get_cache_service(self, redis: Redis) -> CacheService:
        return CacheService(redis)

    @provide(scope=Scope.REQUEST)
    def get_attachment_service(
        self,
        attmt_repo: IAttachmentRepository,
        storage: StorageService,
        task_repo: ITaskRepository,
    ) -> AttachmentService:
        return AttachmentService(attmt_repo, storage, task_repo)


@pytest.fixture(scope="session")
async def container() -> AsyncIterable:
    container = make_async_container(
        TestDatabaseProvider(),
        RepositoryProvider(),
        TestServiceProvider(),
        AuthProvider(),
    )
    yield container
    await container.close()


@pytest.fixture(scope="session", autouse=True)
def mock_celery_tasks():
    with (
        patch("src.services.task_email.send_welcome_email_task.delay"),
        patch("src.services.task_email.send_daily_summary_email.delay"),
    ):
        yield


@pytest.fixture(scope="session", autouse=True)
async def setup_db(container):
    engine = await container.get(AsyncEngine)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
async def client(container) -> AsyncIterable[AsyncClient]:
    from dishka.integrations.fastapi import setup_dishka

    setup_dishka(container, app)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
