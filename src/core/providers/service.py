from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from src.repository.base import (
    IAttachmentRepository,
    ITaskRepository,
    ITaskTagRepository,
)
from src.services.attachment import AttachmentService
from src.services.cache import CacheService
from src.services.storage import StorageService
from src.services.task import TaskService


class ServiceProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_task_service(
        self, task_repo: ITaskRepository, tag_repo: ITaskTagRepository
    ) -> TaskService:
        return TaskService(task_repo, tag_repo)

    @provide(scope=Scope.APP)
    def get_storage_service(self) -> StorageService:
        return StorageService()

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
