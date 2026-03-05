from typing import List

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Request, status

from src.core.limiter import limiter
from src.models.user import UserModel
from src.repository.base import ICategoryRepository
from src.schemas.category import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/categories", tags=["categories"], route_class=DishkaRoute)


@router.get("/get-categories")
@limiter.limit("5/minute")
async def get_categories(
    request: Request,
    repo: FromDishka[ICategoryRepository],
    current_user: FromDishka[UserModel],
) -> List[CategoryResponse]:
    return await repo.get_all(current_user.id)


@router.post("/create-category", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_category(
    request: Request,
    repo: FromDishka[ICategoryRepository],
    category_in: CategoryCreate,
    current_user: FromDishka[UserModel],
) -> CategoryResponse:
    return await repo.create(current_user.id, category_in)
