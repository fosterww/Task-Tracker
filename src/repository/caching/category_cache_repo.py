import hashlib
import json
from typing import List, Tuple

from src.core.exceptions import CacheError
from src.core.logger import logger
from src.models.category import CategoryModel
from src.schemas.category import CategoryCreate, CategoryResponse
from src.services.cache import CacheService
from src.repository.base import ICategoryRepository


class CachingCategoryRepository:
    def __init__(self, repo: ICategoryRepository, cache: CacheService):
        self._repo = repo
        self._cache = cache

    async def get_all(
        self,
        user_id: int,
        offset: int,
        limit: int,
        search: str | None,
    ) -> Tuple[List[CategoryModel], int]:
        params = f"{offset}:{limit}:{search}"
        hash_params = hashlib.sha256(params.encode()).hexdigest()
        cache_key = f"category:user:{user_id}:params:{hash_params}"

        try:
            cached_value = await self._cache.get(cache_key)
            if cached_value:
                data = json.loads(cached_value)
                deserialized_items = [
                    CategoryModel(**CategoryResponse.model_validate(item).model_dump())
                    for item in data["items"]
                ]
                return deserialized_items, data["total"]
        except (CacheError, Exception):
            pass

        items, total = await self._repo.get_all(user_id, offset, limit, search)

        try:
            serializable_items = [
                CategoryResponse.model_validate(item).model_dump(mode="json")
                for item in items
            ]
            cache_payload = json.dumps({"items": serializable_items, "total": total})
            await self._cache.set(cache_key, cache_payload, ttl=3600)
        except Exception as e:
            logger.warning(f"Failed to cache categories for user {user_id}: {e}")

        return items, total

    async def create(
        self, user_id: int, category_data: CategoryCreate
    ) -> CategoryModel:
        category = await self._repo.create(user_id, category_data)
        try:
            pattern = f"category:user:{user_id}:*"
            await self._cache.delete_pattern(pattern)
        except Exception as e:
            logger.warning(f"Failed to invalidate cache for user {user_id}: {e}")
        return category
