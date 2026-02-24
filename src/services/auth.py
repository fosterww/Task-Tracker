from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from src.core.config import settings
from src.core.exceptions import AuthenticationError, UserAlreadyExistsError
from src.core.logger import logger
from src.core.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
)
from src.repository.base import ITokenRepository, IUserRepository
from src.schemas.user import UserCreate, UserResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def register_user(
    user_data: UserCreate, user_repo: IUserRepository
) -> UserResponse:
    existing_user = await user_repo.get_by_email(user_data.email)
    if existing_user:
        logger.warning(f"Registration attempt failed: email {user_data.email} taken")
        raise UserAlreadyExistsError()

    new_user = await user_repo.create(user_data)
    logger.info(f"New user registered: {new_user.email}")

    return UserResponse.model_validate(new_user)


async def login_user(
    form_data: OAuth2PasswordRequestForm,
    user_repo: IUserRepository,
    token_repo: ITokenRepository,
):
    user = await user_repo.get_by_email(form_data.username)

    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.info(f"Failed login attempt for email: {form_data.username}")
        raise AuthenticationError("Incorrect email or password")

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})

    expires_at = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    await token_repo.create(refresh_token, user.id, expires_at)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


async def refresh_access_token(
    token: str, user_repo: IUserRepository, token_repo: ITokenRepository
):
    db_token = await token_repo.get_by_token(token)

    if not db_token or db_token.is_expired():
        raise HTTPException(status_code=401, detail="Refresh token invalid or expired")

    user = await user_repo.get_by_id(db_token.user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    new_access = create_access_token(data={"sub": str(user.id)})
    return {"access_token": new_access, "token_type": "bearer"}
