from typing import List

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, status

from src.models.user import UserModel
from src.repository.base import ICategoryRepository
from src.schemas.category import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/categories", tags=["categories"], route_class=DishkaRoute)


@router.get("/")
async def get_categories(
    repo: FromDishka[ICategoryRepository], current_user: FromDishka[UserModel]
) -> List[CategoryResponse]:
    return await repo.get_all(current_user.id)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_category(
    repo: FromDishka[ICategoryRepository],
    category_in: CategoryCreate,
    current_user: FromDishka[UserModel],
) -> CategoryResponse:
    return await repo.create(current_user.id, category_in)
