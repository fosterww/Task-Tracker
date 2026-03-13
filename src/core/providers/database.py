from typing import Any, AsyncGenerator

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    AsyncSession,
    create_async_engine,
)
from redis.asyncio import Redis

from src.core.config import dbsettings, srcsettings


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def get_engine(self) -> AsyncEngine:
        return create_async_engine(dbsettings.DATABASE_URL)

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
        return Redis(
            host=srcsettings.REDIS_HOST,
            port=srcsettings.REDIS_PORT,
            db=srcsettings.REDIS_DB,
            decode_responses=True,
        )
