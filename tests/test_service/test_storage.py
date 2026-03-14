import pytest
from unittest.mock import AsyncMock, patch

from fastapi import UploadFile
from botocore.exceptions import ClientError

from src.services.storage import StorageService
from src.core.exceptions import StorageError


@pytest.fixture
def storage_service() -> StorageService:
    return StorageService()


@pytest.fixture
def mock_s3_client():
    client = AsyncMock()
    client.generate_presigned_url.return_value = "http://fake-url.com/file"
    return client


@pytest.mark.asyncio
@patch("src.services.storage.StorageService._get_client")
async def test_ensure_bucket_exists(mock_get_client, storage_service, mock_s3_client):
    mock_get_client.return_value.__aenter__.return_value = mock_s3_client

    await storage_service.ensure_bucket("test_bucket")

    mock_s3_client.head_bucket.assert_called_once_with(Bucket="test_bucket")
    mock_s3_client.create_bucket.assert_not_called()


@pytest.mark.asyncio
@patch("src.services.storage.StorageService._get_client")
async def test_ensure_bucket_not_exists(
    mock_get_client, storage_service, mock_s3_client
):
    mock_get_client.return_value.__aenter__.return_value = mock_s3_client

    error_response = {"Error": {"Code": "404", "Message": "Not Found"}}
    mock_s3_client.head_bucket.side_effect = ClientError(error_response, "HeadBucket")

    await storage_service.ensure_bucket("test_bucket")

    mock_s3_client.head_bucket.assert_called_once_with(Bucket="test_bucket")
    mock_s3_client.create_bucket.assert_called_once_with(Bucket="test_bucket")


@pytest.mark.asyncio
@patch("src.services.storage.StorageService._get_client")
@patch("asyncio.sleep", new_callable=AsyncMock)
async def test_ensure_bucket_retries_and_fails(
    mock_sleep, mock_get_client, storage_service, mock_s3_client
):
    mock_get_client.return_value.__aenter__.return_value = mock_s3_client

    mock_s3_client.head_bucket.side_effect = ConnectionRefusedError(
        "Connection refused"
    )

    with pytest.raises(StorageError):
        await storage_service.ensure_bucket("test_bucket")

    assert mock_s3_client.head_bucket.call_count == 5


@pytest.mark.asyncio
@patch("src.services.storage.StorageService._get_client")
async def test_upload_file_success(mock_get_client, storage_service, mock_s3_client):
    mock_get_client.return_value.__aenter__.return_value = mock_s3_client

    dummy_file = AsyncMock(spec=UploadFile)
    dummy_file.read.return_value = b"file content"
    dummy_file.content_type = "text/plain"

    result = await storage_service.upload_file(dummy_file, "test_file.txt")

    assert result == "test_file.txt"
    mock_s3_client.put_object.assert_called_once_with(
        Bucket=storage_service.bucket_name,
        Key="test_file.txt",
        Body=b"file content",
        ContentType="text/plain",
    )


@pytest.mark.asyncio
@patch("src.services.storage.StorageService._get_client")
async def test_upload_file_client_error(
    mock_get_client, storage_service, mock_s3_client
):
    mock_get_client.return_value.__aenter__.return_value = mock_s3_client

    dummy_file = AsyncMock(spec=UploadFile)
    dummy_file.read.return_value = b"file content"
    dummy_file.content_type = "text/plain"

    error_response = {"Error": {"Code": "500", "Message": "Internal Error"}}
    mock_s3_client.put_object.side_effect = ClientError(error_response, "PutObject")

    with pytest.raises(StorageError):
        await storage_service.upload_file(dummy_file, "test_file.txt")


@pytest.mark.asyncio
@patch("src.services.storage.StorageService._get_client")
async def test_get_file_url_success(mock_get_client, storage_service, mock_s3_client):
    mock_get_client.return_value.__aenter__.return_value = mock_s3_client

    url = await storage_service.get_file_url("test_file.txt", expires_in_hours=2)

    assert url == "http://fake-url.com/file"
    mock_s3_client.generate_presigned_url.assert_called_once_with(
        "get_object",
        Params={"Bucket": storage_service.bucket_name, "Key": "test_file.txt"},
        ExpiresIn=2 * 3600,
    )


@pytest.mark.asyncio
@patch("src.services.storage.StorageService._get_client")
async def test_get_file_url_client_error(
    mock_get_client, storage_service, mock_s3_client
):
    mock_get_client.return_value.__aenter__.return_value = mock_s3_client

    error_response = {"Error": {"Code": "403", "Message": "Access Denied"}}
    mock_s3_client.generate_presigned_url.side_effect = ClientError(
        error_response, "GeneratePresignedUrl"
    )

    with pytest.raises(StorageError):
        await storage_service.get_file_url("test_file.txt")


@pytest.mark.asyncio
@patch("src.services.storage.StorageService._get_client")
async def test_delete_file_success(mock_get_client, storage_service, mock_s3_client):
    mock_get_client.return_value.__aenter__.return_value = mock_s3_client

    await storage_service.delete_file("test_file.txt")

    mock_s3_client.delete_object.assert_called_once_with(
        Bucket=storage_service.bucket_name, Key="test_file.txt"
    )


@pytest.mark.asyncio
@patch("src.services.storage.StorageService._get_client")
async def test_delete_file_client_error(
    mock_get_client, storage_service, mock_s3_client
):
    mock_get_client.return_value.__aenter__.return_value = mock_s3_client

    error_response = {"Error": {"Code": "500", "Message": "Internal Error"}}
    mock_s3_client.delete_object.side_effect = ClientError(
        error_response, "DeleteObject"
    )

    with pytest.raises(StorageError):
        await storage_service.delete_file("test_file.txt")
