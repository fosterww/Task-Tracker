from unittest.mock import AsyncMock, MagicMock

import pytest

from src.schemas.task import TaskCreate
from src.services.task import TaskService


@pytest.mark.asyncio
async def test_create_task_success():
    mock_task_repo = AsyncMock()
    mock_tag_repo = AsyncMock()

    service = TaskService(mock_task_repo, mock_tag_repo)

    user_id = 1
    task_data = TaskCreate(title="Test Task", tags=["Test", "mock"])
    mock_tags = ["tag_obj_1", "tag_obj_2"]

    expected_task = MagicMock(id=101, title="Test Task")

    mock_tag_repo.create_or_get.return_value = mock_tags
    mock_task_repo.create.return_value = expected_task

    result = await service.create_task(user_id, task_data)

    mock_tag_repo.create_or_get.assert_called_once_with(task_data.tags)

    mock_task_repo.create.assert_called_once_with(user_id, task_data, tags=mock_tags)

    assert result == expected_task
    assert result.id == 101
