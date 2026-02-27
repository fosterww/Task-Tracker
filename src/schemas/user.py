from pydantic import BaseModel, ConfigDict, EmailStr, field_validator

from .task import TaskResponse


class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_not_to_long(cls, v: str) -> str:
        if v and len(v) < 8:
            raise ValueError("Password too short. (greater than 8 characters)")
        return v


class UserLogin(BaseModel):
    username: str
    hashed_password: str


class UserResponse(BaseModel):
    id: int
    username: str
    tasks: list[TaskResponse] = []
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
