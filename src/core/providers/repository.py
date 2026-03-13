from dishka import Provider, Scope, provide, decorate
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.base import (
    IAttachmentRepository,
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
from src.repository.attachment_repo import SQLAlachemyAttachmentRepository
from src.services.cache import CacheService
from src.repository.caching.task_cache_repo import CachingTaskRepository
from src.repository.caching.category_cache_repo import CachingCategoryRepository


class RepositoryProvider(Provider):
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
    def get_attachment_repo(self, session: AsyncSession) -> IAttachmentRepository:
        return SQLAlachemyAttachmentRepository(session)

    @decorate
    def decorate_task_repo(
        self, source: ITaskRepository, cache: CacheService
    ) -> ITaskRepository:
        return CachingTaskRepository(source, cache)

    @decorate
    def decorate_category_repo(
        self, source: ICategoryRepository, cache: CacheService
    ) -> ICategoryRepository:
        return CachingCategoryRepository(source, cache)
