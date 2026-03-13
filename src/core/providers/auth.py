from dishka import Provider, Scope, provide, from_context
from fastapi import HTTPException, Request, status
from jose import JWTError, jwt

from src.core.config import settings
from src.models.user import UserModel
from src.repository.base import IUserRepository


class AuthProvider(Provider):
    request = from_context(provides=Request, scope=Scope.REQUEST)

    @provide(scope=Scope.REQUEST)
    async def get_current_user(
        self, request: Request, user_repo: IUserRepository
    ) -> UserModel:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
            )
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            id = payload.get("sub")
            if id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )
            user_id = int(id)
        except (JWTError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        user = await user_repo.get_by_id(user_id)

        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user
