from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from src.core.limiter import limiter
from src.repository.base import ITokenRepository, IUserRepository
from src.schemas.user import (
    AccessTokenResponse,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from src.services.auth import login_user, refresh_access_token, register_user

router = APIRouter(prefix="/auth", tags=["auth"], route_class=DishkaRoute)


@router.post("/register")
@limiter.limit("5/minute")
async def register_endpoint(
    user_in: UserCreate, user_repo: FromDishka[IUserRepository], request: Request
) -> UserResponse:
    return await register_user(user_in, user_repo)


@router.post("/login")
@limiter.limit("5/minute")
async def login_endpoint(
    request: Request,
    user_repo: FromDishka[IUserRepository],
    token_repo: FromDishka[ITokenRepository],
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> TokenResponse:
    return await login_user(form_data, user_repo, token_repo)


@router.post("/refresh")
@limiter.limit("5/minute")
async def refresh_token_endpoint(
    refresh_token: str,
    request: Request,
    user_repo: FromDishka[IUserRepository],
    token_repo: FromDishka[ITokenRepository],
) -> AccessTokenResponse:
    return await refresh_access_token(refresh_token, user_repo, token_repo)
