import hashlib
import json
from typing import List, Tuple

from src.core.exceptions import CacheError
from src.core.logger import logger
from src.models.task import TaskModel, TaskPriority, TaskStatus, TaskTagModel
from src.schemas.task import TaskBase, TaskCreate, TaskResponse
from src.services.cache import CacheService
from src.repository.base import ITaskRepository


class CachingTaskRepository:
    def __init__(self, repo: ITaskRepository, cache: CacheService):
        self._repo = repo
        self._cache = cache

    async def get_all(
        self,
        user_id: int,
        offset: int,
        limit: int,
        search: str | None,
        status: TaskStatus | None = None,
        category_id: int | None = None,
        priority: TaskPriority | None = None,
    ) -> Tuple[List[TaskModel], int]:
        params = f"{offset}:{limit}:{search}:{status}:{category_id}:{priority}"
        hash_params = hashlib.md5(params.encode()).hexdigest()
        cache_key = f"task:user:{user_id}:params:{hash_params}"

        try:
            cached_value = await self._cache.get(cache_key)
            if cached_value:
                data = json.loads(cached_value)
                deserialized_items = [
                    TaskModel(
                        **TaskResponse.model_validate(item).model_dump(
                            exclude={"category", "subtasks", "tags", "attachments"}
                        )
                    )
                    for item in data["items"]
                ]
                return deserialized_items, data["total"]
        except (CacheError, Exception):
            pass

        items, total = await self._repo.get_all(
            user_id, offset, limit, search, status, category_id, priority
        )

        try:
            serializable_items = [
                TaskResponse.model_validate(item).model_dump(mode="json")
                for item in items
            ]
            cache_payload = json.dumps({"items": serializable_items, "total": total})
            await self._cache.set(cache_key, cache_payload, ttl=3600)
        except Exception as e:
            logger.warning(f"Failed to cache tasks for user {user_id}: {e}")

        return items, total

    async def create(
        self,
        user_id: int,
        task_data: TaskCreate,
        tags: list[TaskTagModel] | None = None,
    ) -> TaskModel:
        task = await self._repo.create(user_id, task_data, tags)
        try:
            pattern = f"task:user:{user_id}:*"
            await self._cache.delete_pattern(pattern)
        except Exception as e:
            logger.warning(f"Failed to invalidate cache for user {user_id}: {e}")
        return task

    async def get_by_id(self, task_id: int, user_id: int) -> TaskModel | None:
        cache_key = f"task:user:{user_id}:id:{task_id}"
        try:
            cached_value = await self._cache.get(cache_key)
            if cached_value:
                data = json.loads(cached_value)
                return TaskModel(
                    **TaskResponse.model_validate(data).model_dump(
                        exclude={"category", "subtasks", "tags", "attachments"}
                    )
                )
        except (CacheError, Exception):
            pass

        task = await self._repo.get_by_id(task_id, user_id)

        if task:
            try:
                cache_payload = json.dumps(
                    TaskResponse.model_validate(task).model_dump(mode="json")
                )
                await self._cache.set(cache_key, cache_payload, ttl=3600)
            except Exception as e:
                logger.warning(f"Failed to cache task {task_id}: {e}")
        return task

    async def update(
        self, task_id: int, user_id: int, task_data: TaskBase
    ) -> TaskModel:
        task = await self._repo.update(task_id, user_id, task_data)
        try:
            pattern = f"task:user:{user_id}:*"
            await self._cache.delete_pattern(pattern)
        except Exception as e:
            logger.warning(f"Failed to invalidate cache for user {user_id}: {e}")
        return task

    async def delete(self, task_id: int, user_id: int) -> None:
        await self._repo.delete(task_id, user_id)
        try:
            pattern = f"task:user:{user_id}:*"
            await self._cache.delete_pattern(pattern)
        except Exception as e:
            logger.warning(f"Failed to invalidate cache for user {user_id}: {e}")
