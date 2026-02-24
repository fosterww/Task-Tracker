from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.repository.base import ITokenRepository, IUserRepository
from src.schemas.user import TokenResponse, UserCreate, UserResponse
from src.services.auth import login_user, refresh_access_token, register_user

router = APIRouter(prefix='/auth', tags=['auth'], route_class=DishkaRoute)


@router.post("/register")
async def register_endpoint(
    user_in: UserCreate,
    user_repo: FromDishka[IUserRepository]
) -> UserResponse:
    return await register_user(user_in, user_repo)


@router.post("/login")
async def login_endpoint(
    user_repo: FromDishka[IUserRepository],
    token_repo: FromDishka[ITokenRepository],
    form_data: OAuth2PasswordRequestForm = Depends()
) -> TokenResponse:
    return await login_user(form_data, user_repo, token_repo)


@router.post("/refresh")
async def refresh_token_endpoint(
    refresh_token: str,
    user_repo: FromDishka[IUserRepository],
    token_repo: FromDishka[ITokenRepository]
) -> TokenResponse:
    return await refresh_access_token(refresh_token, user_repo, token_repo)
