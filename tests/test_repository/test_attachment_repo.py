from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.core.exceptions import (
    AppError,
    AttachmentNotFoundError,
    DatabaseIntegrityError,
)
from src.models.task import TaskAttachments
from src.repository.attachment_repo import SQLAlachemyAttachmentRepository


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def attachment_repo(mock_session):
    return SQLAlachemyAttachmentRepository(session=mock_session)


@pytest.mark.asyncio
async def test_get_by_task_success(attachment_repo, mock_session):
    mock_attachment1 = TaskAttachments(id=1, filename="test1.png", task_id=1)
    mock_attachment2 = TaskAttachments(id=2, filename="test2.png", task_id=1)

    mock_result = MagicMock()
    mock_result.scalars().all.return_value = [mock_attachment1, mock_attachment2]
    mock_session.execute.return_value = mock_result

    result = await attachment_repo.get_by_task(user_id=1, task_id=1)

    assert len(result) == 2
    assert result[0].filename == "test1.png"
    assert result[1].filename == "test2.png"
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_task_sql_error(attachment_repo, mock_session):
    mock_session.execute.side_effect = SQLAlchemyError("DB error")

    with pytest.raises(AppError, match="Cannot list all tasks"):
        await attachment_repo.get_by_task(user_id=1, task_id=1)


@pytest.mark.asyncio
async def test_get_by_id_success(attachment_repo, mock_session):
    mock_attachment = TaskAttachments(id=1, filename="test.png", task_id=1)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_attachment
    mock_session.execute.return_value = mock_result

    result = await attachment_repo.get_by_id(user_id=1, attachment_id=1)

    assert result.id == 1
    assert result.filename == "test.png"
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_not_found(attachment_repo, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    with pytest.raises(AttachmentNotFoundError):
        await attachment_repo.get_by_id(user_id=1, attachment_id=1)

    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_sql_error(attachment_repo, mock_session):
    mock_session.execute.side_effect = SQLAlchemyError("DB error")

    with pytest.raises(AppError, match="Cannot list all tasks"):
        await attachment_repo.get_by_id(user_id=1, attachment_id=1)


@pytest.mark.asyncio
async def test_delete_success(attachment_repo, mock_session):
    mock_attachment = TaskAttachments(id=1, filename="test.png", task_id=1)

    await attachment_repo.delete(mock_attachment)

    mock_session.delete.assert_called_once_with(mock_attachment)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_sql_error(attachment_repo, mock_session):
    mock_attachment = TaskAttachments(id=1, filename="test.png", task_id=1)
    mock_session.commit.side_effect = SQLAlchemyError("DB error")

    with pytest.raises(AppError, match="Cannot list all tasks"):
        await attachment_repo.delete(mock_attachment)


@pytest.mark.asyncio
async def test_create_success(attachment_repo, mock_session):
    result = await attachment_repo.create(
        task_id=1,
        filename="test.png",
        s3_key="random-key.png",
        size=1024,
        content_type="image/png",
    )

    assert result.filename == "test.png"
    assert result.s3_key == "random-key.png"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_integrity_error(attachment_repo, mock_session):
    mock_session.commit.side_effect = IntegrityError(
        None, None, Exception("Unique constraint failed")
    )

    with pytest.raises(DatabaseIntegrityError, match="Data constraints violated"):
        await attachment_repo.create(
            task_id=1,
            filename="test.png",
            s3_key="random-key.png",
            size=1024,
            content_type="image/png",
        )

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_sql_error(attachment_repo, mock_session):
    mock_session.commit.side_effect = SQLAlchemyError("DB error")

    with pytest.raises(AppError, match="Cannot list all tasks"):
        await attachment_repo.create(
            task_id=1,
            filename="test.png",
            s3_key="random-key.png",
            size=1024,
            content_type="image/png",
        )
