from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, File, Request, UploadFile, status

from src.schemas.task import TaskAttachmentResponse
from src.models.user import UserModel
from src.core.limiter import limiter
from src.services.attachment import AttachmentService


router = APIRouter(
    prefix="/tasks/{task_id}/attachments", tags=["Attachments"], route_class=DishkaRoute
)


@router.post("", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def upload_attachment_endpoint(
    request: Request,
    current_user: FromDishka[UserModel],
    service: FromDishka[AttachmentService],
    task_id: int,
    file: UploadFile = File(...),
) -> TaskAttachmentResponse:
    return await service.create_attachment(
        file=file, task_id=task_id, user_id=current_user.id
    )


@router.get("")
@limiter.limit("5/minute")
async def list_attachment_endpoint(
    request: Request,
    service: FromDishka[AttachmentService],
    current_user: FromDishka[UserModel],
    task_id: int,
) -> list[TaskAttachmentResponse]:
    return await service.get_task_attachments(task_id=task_id, user_id=current_user.id)


@router.get("/{attachment_id}/url")
@limiter.limit("5/minute")
async def get_attachment_url_endpoint(
    request: Request,
    service: FromDishka[AttachmentService],
    current_user: FromDishka[UserModel],
    attachment_id: int,
) -> str:
    return await service.get_attachment_url(
        attachment_id=attachment_id, user_id=current_user.id
    )


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/minute")
async def delete_attachment_endpoint(
    request: Request,
    attachment_id: int,
    current_user: FromDishka[UserModel],
    service: FromDishka[AttachmentService],
) -> None:
    return await service.delete_attachment(
        user_id=current_user.id, attachment_id=attachment_id
    )
