from typing import AsyncIterable

import pytest
from dishka import Scope, make_async_container, provide
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    create_async_engine,
)

from src.core.ioc import AppProvider
from src.database import Base
from src.main import app


class TestAppProvider(AppProvider):
    @provide(scope=Scope.APP)
    def get_engine(self) -> AsyncEngine:
        return create_async_engine(
            "sqlite+aiosqlite:///:memory:", connect_args={"check_same_thread": False}
        )


@pytest.fixture(scope="session")
async def container() -> AsyncIterable:
    container = make_async_container(TestAppProvider())
    yield container
    await container.close()


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
