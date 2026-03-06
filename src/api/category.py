from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, Request, status

from src.core.limiter import limiter
from src.models.user import UserModel
from src.repository.base import ICategoryRepository
from src.schemas.category import CategoryCreate, CategoryResponse
from src.schemas.pagination import PaginatedResponse, PaginationParams

router = APIRouter(prefix="/categories", tags=["categories"], route_class=DishkaRoute)


@router.get("/get-categories")
@limiter.limit("5/minute")
async def get_categories(
    request: Request,
    repo: FromDishka[ICategoryRepository],
    current_user: FromDishka[UserModel],
    params: PaginationParams = Depends(),
) -> PaginatedResponse[CategoryResponse]:
    items, total = await repo.get_all(
        current_user.id, params.skip, params.limit, params.search
    )
    return PaginatedResponse.create(items, total, params.offset, params.limit)


@router.post("/create-category", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_category(
    request: Request,
    repo: FromDishka[ICategoryRepository],
    category_in: CategoryCreate,
    current_user: FromDishka[UserModel],
) -> CategoryResponse:
    return await repo.create(current_user.id, category_in)
