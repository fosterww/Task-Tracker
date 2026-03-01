from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.core.exceptions import AppError, DatabaseIntegrityError, TaskNotFoundError
from src.models.task import TaskModel, TaskTagModel
from src.repository.task_repo import SQLAlchemyTaskRepository
from src.schemas.task import TaskBase, TaskCreate


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def task_repo(mock_session):
    return SQLAlchemyTaskRepository(session=mock_session)


@pytest.mark.asyncio
async def test_get_all_success(task_repo, mock_session):
    mock_task = TaskModel(id=1, title="Test Task", author_id=1)
    mock_task1 = TaskModel(id=2, title="Test Task1", author_id=1)

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_task, mock_task1
    mock_session.execute.return_value = mock_result

    task = await task_repo.get_all(user_id=1)

    assert task == [mock_task, mock_task1]
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_status_success(task_repo, mock_session):
    mock_task = TaskModel(id=1, title="Test Task", status="pending", author_id=1)
    mock_task1 = TaskModel(id=2, title="Test Task1", priority="low", author_id=1)
    mock_task2 = TaskModel(id=3, title="Test Task3", author_id=1)

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = (
        mock_task,
        mock_task1,
        mock_task2,
    )
    mock_session.execute.return_value = mock_result

    task = await task_repo.get_all(user_id=1, status="pending")

    assert task == [mock_task, mock_task1, mock_task2]
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_priority_success(task_repo, mock_session):
    mock_task = TaskModel(id=1, title="Test Task", status="pending", author_id=1)
    mock_task1 = TaskModel(id=2, title="Test Task1", priority="low", author_id=1)
    mock_task2 = TaskModel(id=3, title="Test Task3", author_id=1)

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = (
        mock_task1,
        mock_task,
        mock_task2,
    )
    mock_session.execute.return_value = mock_result

    task = await task_repo.get_all(user_id=1, priority="low")

    assert task == [mock_task1, mock_task, mock_task2]
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_category_success(task_repo, mock_session):
    mock_task = TaskModel(id=1, title="Test Task", status="pending", author_id=1)
    mock_task1 = TaskModel(id=2, title="Test Task1", priority="low", author_id=1)
    mock_task2 = TaskModel(id=3, title="Test Task3", category_id=1, author_id=1)

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = (
        mock_task2,
        mock_task,
        mock_task1,
    )
    mock_session.execute.return_value = mock_result

    task = await task_repo.get_all(user_id=1, category_id=1)

    assert task == [mock_task2, mock_task, mock_task1]
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_sql_error(task_repo, mock_session):
    mock_session.execute.side_effect = SQLAlchemyError("DB error")

    with pytest.raises(AppError, match="Cannot list all tasks"):
        await task_repo.get_all(1)


@pytest.mark.asyncio
async def test_create_success(task_repo, mock_session):
    task_data = TaskCreate(title="New Task", description="A description")
    mock_task = TaskModel(
        id=1, title="New Task", description="A description", author_id=1
    )

    mock_result = MagicMock()
    mock_result.scalar_one.return_value = mock_task
    mock_session.execute.return_value = mock_result

    task = await task_repo.create(user_id=1, task_data=task_data)

    assert task == mock_task
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_with_tags_success(task_repo, mock_session):
    task_data = TaskCreate(title="New Task", description="A description")
    mock_task = TaskModel(
        id=1,
        title="New Task",
        description="A description",
        tags=[TaskTagModel(id=1, name="Test")],
        author_id=1,
    )
    task_tags = [TaskTagModel(id=1, name="Test")]

    mock_result = MagicMock()
    mock_result.scalar_one.return_value = mock_task
    mock_session.execute.return_value = mock_result

    task = await task_repo.create(user_id=1, task_data=task_data, tags=task_tags)

    assert task == mock_task
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_integrity_error(task_repo, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = []
    mock_session.execute.return_value = mock_result
    mock_session.commit.side_effect = IntegrityError(
        None, None, Exception("Unique constraint failed")
    )

    task_data = TaskCreate(title="New Task", description="A description")

    with pytest.raises(
        DatabaseIntegrityError, match="Invalid category_id or data constraints violated"
    ):
        await task_repo.create(user_id=1, task_data=task_data)

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_sql_error(task_repo, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one.return_value = []
    mock_session.execute.return_value = mock_result
    mock_session.commit.side_effect = SQLAlchemyError("Generic DB error")

    task_data = TaskCreate(title="New Task", description="A description")

    with pytest.raises(AppError, match="Internal database error"):
        await task_repo.create(user_id=1, task_data=task_data)

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_success(task_repo, mock_session):
    mock_task = TaskModel(
        id=1, title="New Task", description="A description", author_id=1
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_task
    mock_session.execute.return_value = mock_result

    task = await task_repo.get_by_id(1, 1)

    assert task == mock_task
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_not_found(task_repo, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    with pytest.raises(TaskNotFoundError):
        await task_repo.get_by_id(1, 1)

    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_sql_error(task_repo, mock_session):
    mock_session.execute.side_effect = SQLAlchemyError("DB error")

    with pytest.raises(AppError, match="Error while getting task from db"):
        await task_repo.get_by_id(1, 1)


@pytest.mark.asyncio
async def test_update_success(task_repo, mock_session):
    mock_task = TaskModel(
        id=1, title="Old Task", description="Old description", author_id=1
    )
    updated_task = TaskModel(
        id=1, title="Updated Task", description="Old description", author_id=1
    )
    task_data = TaskBase(title="Updated Task")

    mock_result_get = MagicMock()
    mock_result_get.scalar_one_or_none.return_value = mock_task

    mock_result_update = MagicMock()
    mock_result_update.scalar_one.return_value = updated_task

    mock_session.execute.side_effect = [mock_result_get, mock_result_update]

    task = await task_repo.update(task_id=1, user_id=1, task_data=task_data)

    assert task == updated_task
    assert mock_session.execute.call_count == 2
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_not_found(task_repo, mock_session):
    task_data = TaskBase(title="Updated Task")

    mock_result_get = MagicMock()
    mock_result_get.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result_get

    with pytest.raises(TaskNotFoundError):
        await task_repo.update(task_id=1, user_id=1, task_data=task_data)


@pytest.mark.asyncio
async def test_update_integrity_error(task_repo, mock_session):
    mock_task = TaskModel(
        id=1, title="Old Task", description="Old description", author_id=1
    )
    task_data = TaskBase(title="Updated Task")

    mock_result_get = MagicMock()
    mock_result_get.scalar_one_or_none.return_value = mock_task

    mock_session.execute.return_value = mock_result_get
    mock_session.commit.side_effect = IntegrityError(
        None, None, Exception("Unique constraint failed")
    )

    with pytest.raises(DatabaseIntegrityError, match="Invalid data for update"):
        await task_repo.update(task_id=1, user_id=1, task_data=task_data)

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_sql_error(task_repo, mock_session):
    mock_task = TaskModel(
        id=1, title="Old Task", description="Old description", author_id=1
    )
    task_data = TaskBase(title="Updated Task")

    mock_result_get = MagicMock()
    mock_result_get.scalar_one_or_none.return_value = mock_task

    mock_session.execute.return_value = mock_result_get
    mock_session.commit.side_effect = SQLAlchemyError("Generic DB error")

    with pytest.raises(AppError, match="Failed to update task"):
        await task_repo.update(task_id=1, user_id=1, task_data=task_data)

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_success(task_repo, mock_session):
    mock_task = TaskModel(id=1, title="Task to delete", author_id=1)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_task
    mock_session.execute.return_value = mock_result

    await task_repo.delete(task_id=1, user_id=1)

    mock_session.execute.assert_awaited_once()
    mock_session.delete.assert_called_once_with(mock_task)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_not_found(task_repo, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    with pytest.raises(TaskNotFoundError):
        await task_repo.delete(task_id=1, user_id=1)

    mock_session.execute.assert_awaited_once()
    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_delete_sql_error(task_repo, mock_session):
    mock_session.execute.side_effect = SQLAlchemyError("DB error")

    with pytest.raises(AppError, match="Internal database error"):
        await task_repo.delete(task_id=1, user_id=1)

    mock_session.rollback.assert_awaited_once()
