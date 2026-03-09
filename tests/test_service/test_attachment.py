from unittest.mock import AsyncMock, MagicMock
import pytest
from fastapi import HTTPException

from src.core.exceptions import AttachmentNotFoundError
from src.services.attachment import AttachmentService


@pytest.fixture
def mock_attachment_repo():
    return AsyncMock()


@pytest.fixture
def mock_storage_service():
    return AsyncMock()


@pytest.fixture
def mock_task_repo():
    return AsyncMock()


@pytest.fixture
def attachment_service(mock_attachment_repo, mock_storage_service, mock_task_repo):
    return AttachmentService(
        attachemt_repo=mock_attachment_repo,
        storage=mock_storage_service,
        task_repo=mock_task_repo,
    )


@pytest.mark.asyncio
async def test_create_attachment_success(
    attachment_service, mock_attachment_repo, mock_storage_service, mock_task_repo
):
    mock_file = MagicMock()
    mock_file.filename = "test.png"
    mock_file.size = 1024
    mock_file.content_type = "image/png"

    mock_task = MagicMock(id=1)
    mock_task_repo.get_by_id.return_value = mock_task

    mock_attachment = MagicMock(id=1, filename="test.png")
    mock_attachment_repo.create.return_value = mock_attachment

    result = await attachment_service.create_attachment(
        file=mock_file, task_id=1, user_id=1
    )

    assert result == mock_attachment
    mock_task_repo.get_by_id.assert_called_once_with(1, 1)
    mock_storage_service.upload_file.assert_called_once()
    mock_attachment_repo.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_attachment_task_not_found(attachment_service, mock_task_repo):
    mock_file = MagicMock()
    mock_file.filename = "test.png"

    mock_task_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        await attachment_service.create_attachment(file=mock_file, task_id=1, user_id=1)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Task not found"


@pytest.mark.asyncio
async def test_create_attachment_upload_failure(
    attachment_service, mock_storage_service, mock_task_repo
):
    mock_file = MagicMock()
    mock_file.filename = "test.png"

    mock_task = MagicMock(id=1)
    mock_task_repo.get_by_id.return_value = mock_task

    mock_storage_service.upload_file.side_effect = Exception("Upload failed")

    with pytest.raises(HTTPException) as exc:
        await attachment_service.create_attachment(file=mock_file, task_id=1, user_id=1)

    assert exc.value.status_code == 500
    assert exc.value.detail == "File upload failed"


@pytest.mark.asyncio
async def test_delete_attachment_success(
    attachment_service, mock_attachment_repo, mock_storage_service
):
    mock_attachment = MagicMock(id=1, s3_key="key.png")
    mock_attachment_repo.get_by_id.return_value = mock_attachment

    await attachment_service.delete_attachment(attachment_id=1, user_id=1)

    mock_attachment_repo.get_by_id.assert_called_once_with(1, 1)
    mock_storage_service.delete_file.assert_called_once_with("key.png")
    mock_attachment_repo.delete.assert_called_once_with(mock_attachment)


@pytest.mark.asyncio
async def test_delete_attachment_not_found(attachment_service, mock_attachment_repo):
    mock_attachment_repo.get_by_id.return_value = None

    with pytest.raises(AttachmentNotFoundError):
        await attachment_service.delete_attachment(attachment_id=1, user_id=1)


@pytest.mark.asyncio
async def test_get_task_attachments_success(attachment_service, mock_attachment_repo):
    mock_attachments = [MagicMock(id=1), MagicMock(id=2)]
    mock_attachment_repo.get_by_task.return_value = mock_attachments

    result = await attachment_service.get_task_attachments(task_id=1, user_id=1)

    assert result == mock_attachments
    mock_attachment_repo.get_by_task.assert_called_once_with(1, 1)


@pytest.mark.asyncio
async def test_get_attachment_url_success(
    attachment_service, mock_attachment_repo, mock_storage_service
):
    mock_attachment = MagicMock(id=1, s3_key="key.png")
    mock_attachment_repo.get_by_id.return_value = mock_attachment

    mock_storage_service.get_file_url.return_value = "http://example.com/key.png"

    result = await attachment_service.get_attachment_url(attachment_id=1, user_id=1)

    assert result == "http://example.com/key.png"
    mock_attachment_repo.get_by_id.assert_called_once_with(1, 1)
    mock_storage_service.get_file_url.assert_called_once_with("key.png")


@pytest.mark.asyncio
async def test_get_attachment_url_not_found(attachment_service, mock_attachment_repo):
    mock_attachment_repo.get_by_id.return_value = None

    with pytest.raises(AttachmentNotFoundError):
        await attachment_service.get_attachment_url(attachment_id=1, user_id=1)
