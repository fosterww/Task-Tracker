import pytest
from unittest.mock import AsyncMock

from dishka import AsyncContainer
from redis.asyncio import Redis, RedisError

from src.services.cache import CacheService
from src.core.exceptions import CacheError, AppError


@pytest.fixture
async def mock_redis(container: AsyncContainer) -> AsyncMock:
    return await container.get(Redis)


@pytest.fixture
async def cache_service(container: AsyncContainer) -> CacheService:
    return await container.get(CacheService)


@pytest.mark.asyncio
async def test_get_key_success(cache_service: CacheService, mock_redis: AsyncMock):
    mock_redis.get = AsyncMock(return_value="mock_value")

    result = await cache_service.get("test_key")

    assert result == "mock_value"
    mock_redis.get.assert_called_once_with("test_key")


@pytest.mark.asyncio
async def test_get_key_miss(cache_service: CacheService, mock_redis: AsyncMock):
    mock_redis.get = AsyncMock(return_value=None)

    with pytest.raises(CacheError):
        await cache_service.get("test_key")


@pytest.mark.asyncio
async def test_get_key_error(cache_service: CacheService, mock_redis: AsyncMock):
    mock_redis.get = AsyncMock(side_effect=RedisError("Connection lost"))

    with pytest.raises(AppError) as exc_info:
        await cache_service.get("test_key")

    assert "Error getting key for test_key" in str(exc_info.value)


@pytest.mark.asyncio
async def test_set_key_success(cache_service: CacheService, mock_redis: AsyncMock):
    mock_redis.set = AsyncMock(return_value=True)

    await cache_service.set("test_key", "test_value", 3600)

    mock_redis.set.assert_called_once_with("test_key", "test_value", ex=3600)


@pytest.mark.asyncio
async def test_set_key_error(cache_service: CacheService, mock_redis: AsyncMock):
    mock_redis.set = AsyncMock(side_effect=RedisError("Connection lost"))

    with pytest.raises(AppError) as exc_info:
        await cache_service.set("test_key", "test_value", 3600)

    assert "Error set key test_key" in str(exc_info.value)


@pytest.mark.asyncio
async def test_delete_key_success(cache_service: CacheService, mock_redis: AsyncMock):
    mock_redis.delete = AsyncMock(return_value=1)

    await cache_service.delete("test_key")

    mock_redis.delete.assert_called_once_with("test_key")


@pytest.mark.asyncio
async def test_delete_key_miss(cache_service: CacheService, mock_redis: AsyncMock):
    mock_redis.delete = AsyncMock(return_value=0)

    with pytest.raises(CacheError):
        await cache_service.delete("test_key")


@pytest.mark.asyncio
async def test_delete_key_error(cache_service: CacheService, mock_redis: AsyncMock):
    mock_redis.delete = AsyncMock(side_effect=RedisError("Connection lost"))

    with pytest.raises(AppError) as exc_info:
        await cache_service.delete("test_key")

    assert "Error delete key test_key" in str(exc_info.value)


@pytest.mark.asyncio
async def test_delete_pattern_success(
    cache_service: CacheService, mock_redis: AsyncMock
):
    mock_redis.keys = AsyncMock(return_value=["test_key:1", "test_key:2"])
    mock_redis.delete = AsyncMock(return_value=2)

    await cache_service.delete_pattern("test_key:*")

    mock_redis.keys.assert_called_once_with("test_key:*")
    mock_redis.delete.assert_called_once_with("test_key:1", "test_key:2")


@pytest.mark.asyncio
async def test_delete_pattern_miss(cache_service: CacheService, mock_redis: AsyncMock):
    mock_redis.keys = AsyncMock(return_value=[])

    with pytest.raises(CacheError):
        await cache_service.delete_pattern("test_key:*")


@pytest.mark.asyncio
async def test_delete_pattern_error(cache_service: CacheService, mock_redis: AsyncMock):
    mock_redis.keys = AsyncMock(side_effect=RedisError("Connection lost"))

    with pytest.raises(AppError) as exc_info:
        await cache_service.delete_pattern("test_key:*")

    assert "Error delete keys with pattern test_key:*" in str(exc_info.value)
