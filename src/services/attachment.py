import uuid
import os
from fastapi import HTTPException, UploadFile

from src.services.storage import StorageService
from src.repository.base import IAttachmentRepository, ITaskRepository
from src.core.exceptions import AttachmentNotFoundError


class AttachmentService:
    def __init__(
        self,
        attachemt_repo: IAttachmentRepository,
        storage: StorageService,
        task_repo: ITaskRepository,
    ):
        self.storage = storage
        self.attmt_repo = attachemt_repo
        self.task_repo = task_repo

    async def create_attachment(self, file: UploadFile, task_id: int, user_id: int):
        task = await self.task_repo.get_by_id(task_id, user_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        ext = os.path.splitext(file.filename)[1]
        s3_key = f"{uuid.uuid4()}{ext}"

        try:
            await self.storage.upload_file(file, s3_key)
        except Exception:
            raise HTTPException(status_code=500, detail="File upload failed")

        attachment = await self.attmt_repo.create(
            task_id=task_id,
            filename=file.filename,
            s3_key=s3_key,
            size=file.size,
            content_type=file.content_type,
        )
        return attachment

    async def delete_attachment(self, attachment_id: int, user_id: int):
        attachment = await self.attmt_repo.get_by_id(user_id, attachment_id)
        if not attachment:
            raise AttachmentNotFoundError()
        await self.storage.delete_file(attachment.s3_key)
        await self.attmt_repo.delete(attachment)

    async def get_task_attachments(self, task_id: int, user_id: int):
        attachment = await self.attmt_repo.get_by_task(user_id, task_id)
        return attachment

    async def get_attachment_url(self, attachment_id: int, user_id: int):
        attachment = await self.attmt_repo.get_by_id(user_id, attachment_id)
        if not attachment:
            raise AttachmentNotFoundError()
        return await self.storage.get_file_url(attachment.s3_key)
