import asyncio
import aiohttp

from contextlib import asynccontextmanager
from datetime import timedelta

import aioboto3
from botocore.exceptions import ClientError
from fastapi import UploadFile

from src.core.config import srcsettings
from src.core.exceptions import StorageError
from src.core.logger import logger

session = aioboto3.Session()


class StorageService:
    def __init__(self):
        self._s3_config = {
            "service_name": "s3",
            "endpoint_url": srcsettings.S3_ENDPOINT,
            "aws_access_key_id": srcsettings.AWS_ACCESS_KEY_ID,
            "aws_secret_access_key": srcsettings.AWS_SECRET_ACCESS_KEY,
            "region_name": srcsettings.S3_REGION,
        }
        self.bucket_name = srcsettings.S3_BUCKET

    @asynccontextmanager
    async def _get_client(self):
        async with session.client(**self._s3_config) as client:
            yield client

    async def ensure_bucket(self, bucket: str) -> None:
        max_retries = 5
        for i in range(max_retries):
            try:
                async with self._get_client() as s3:
                    try:
                        await s3.head_bucket(Bucket=bucket)
                    except ClientError as exc:
                        error_code = exc.response.get("Error", {}).get("Code")
                        if error_code not in {"404", "NoSuchBucket"}:
                            raise
                        await s3.create_bucket(Bucket=bucket)
                break
            except (aiohttp.ClientError, ConnectionRefusedError, OSError) as e:
                if i == max_retries - 1:
                    logger.error(
                        f"Failed to connect to MinIO after {max_retries} retries: {e}"
                    )
                    raise StorageError() from e
                logger.warning(
                    f"MinIO not ready, retrying in 2 seconds... ({i + 1}/{max_retries})"
                )
                await asyncio.sleep(2)

    async def upload_file(self, file: UploadFile, object_name: str) -> str:
        try:
            data = await file.read()
            async with self._get_client() as s3:
                await s3.put_object(
                    Bucket=self.bucket_name,
                    Key=object_name,
                    Body=data,
                    ContentType=file.content_type or "application/octet-stream",
                )
            return object_name
        except ClientError as e:
            logger.error(f"S3 error: {e}")
            raise StorageError()

    async def get_file_url(self, object_name: str, expires_in_hours: int = 1) -> str:
        try:
            async with self._get_client() as s3:
                url = await s3.generate_presigned_url(
                    "get_object",
                    Params={
                        "Bucket": self.bucket_name,
                        "Key": object_name,
                    },
                    ExpiresIn=int(timedelta(hours=expires_in_hours).total_seconds()),
                )
                return url
        except ClientError as e:
            logger.error(f"S3 error: {e}")
            raise StorageError()

    async def delete_file(self, object_name: str) -> None:
        try:
            async with self._get_client() as s3:
                await s3.delete_object(
                    Bucket=self.bucket_name,
                    Key=object_name,
                )
        except ClientError as e:
            logger.error(f"S3 error: {e}")
            raise StorageError()
