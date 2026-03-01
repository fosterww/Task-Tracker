from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.core.exceptions import AppError, DatabaseIntegrityError, TaskNotFoundError
from src.models.task import SubTaskModel, TaskModel
from src.repository.subtask_repo import SQLAlchemySubTaskRepository
from src.schemas.task import SubTaskCreate


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def subtask_repo(mock_session):
    return SQLAlchemySubTaskRepository(session=mock_session)


@pytest.mark.asyncio
async def test_create_success(subtask_repo, mock_session):
    subtask_data = SubTaskCreate(title="New Subtask")
    mock_task = TaskModel(id=1, author_id=1)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_task
    mock_session.execute.return_value = mock_result

    result = await subtask_repo.create(user_id=1, task_id=1, subtask_data=subtask_data)

    assert result.title == "New Subtask"
    assert result.parent_task_id == 1
    mock_session.execute.assert_awaited_once()
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_task_not_found(subtask_repo, mock_session):
    subtask_data = SubTaskCreate(title="New Subtask")

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    with pytest.raises(TaskNotFoundError):
        await subtask_repo.create(user_id=1, task_id=1, subtask_data=subtask_data)

    mock_session.execute.assert_awaited_once()
    mock_session.add.assert_not_called()


@pytest.mark.asyncio
async def test_create_integrity_error(subtask_repo, mock_session):
    subtask_data = SubTaskCreate(title="New Subtask")
    mock_task = TaskModel(id=1, author_id=1)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_task
    mock_session.execute.return_value = mock_result

    mock_session.commit.side_effect = IntegrityError(
        None, None, Exception("Unique constraint failed")
    )

    with pytest.raises(
        DatabaseIntegrityError, match="Invalid task_id or data constraints violated"
    ):
        await subtask_repo.create(user_id=1, task_id=1, subtask_data=subtask_data)

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_sql_error(subtask_repo, mock_session):
    subtask_data = SubTaskCreate(title="New Subtask")
    mock_session.execute.side_effect = SQLAlchemyError("Generic DB error")

    with pytest.raises(AppError, match="Internal database error"):
        await subtask_repo.create(user_id=1, task_id=1, subtask_data=subtask_data)

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_check_success(subtask_repo, mock_session):
    mock_subtask = SubTaskModel(id=1, title="Subtask", parent_task_id=1, is_done=False)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_subtask
    mock_session.execute.return_value = mock_result

    result = await subtask_repo.check(user_id=1, subtask_id=1)

    assert result.is_done is True
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(mock_subtask)


@pytest.mark.asyncio
async def test_uncheck_success(subtask_repo, mock_session):
    mock_subtask = SubTaskModel(id=1, title="Subtask", parent_task_id=1, is_done=True)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_subtask
    mock_session.execute.return_value = mock_result

    result = await subtask_repo.uncheck(user_id=1, subtask_id=1)

    assert result.is_done is False
    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(mock_subtask)


@pytest.mark.asyncio
async def test_update_status_not_found(subtask_repo, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    with pytest.raises(TaskNotFoundError):
        await subtask_repo.check(user_id=1, subtask_id=1)

    mock_session.execute.assert_awaited_once()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_update_status_sql_error(subtask_repo, mock_session):
    mock_session.execute.side_effect = SQLAlchemyError("Generic DB error")

    with pytest.raises(AppError, match="Internal database error"):
        await subtask_repo.check(user_id=1, subtask_id=1)

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_success(subtask_repo, mock_session):
    mock_subtask = SubTaskModel(id=1, title="Subtask", parent_task_id=1)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_subtask
    mock_session.execute.return_value = mock_result

    await subtask_repo.delete(user_id=1, subtask_id=1)

    mock_session.execute.assert_awaited_once()
    mock_session.delete.assert_called_once_with(mock_subtask)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_not_found(subtask_repo, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    with pytest.raises(TaskNotFoundError):
        await subtask_repo.delete(user_id=1, subtask_id=1)

    mock_session.execute.assert_awaited_once()
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete_sql_error(subtask_repo, mock_session):
    mock_session.execute.side_effect = SQLAlchemyError("Generic DB error")

    with pytest.raises(AppError, match="Internal database error"):
        await subtask_repo.delete(user_id=1, subtask_id=1)

    mock_session.rollback.assert_awaited_once()
