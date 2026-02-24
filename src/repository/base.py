from datetime import datetime
from typing import List, Optional, Protocol

from src.models.category import CategoryModel
from src.models.task import (
    SubTaskModel,
    TaskModel,
    TaskPriority,
    TaskStatus,
    TaskTagModel,
)
from src.models.user import RefreshTokenModel, UserModel
from src.schemas.category import CategoryCreate
from src.schemas.task import SubTaskCreate, TaskBase, TaskCreate
from src.schemas.user import UserCreate


class IUserRepository(Protocol):
    async def get_by_id(self, user_id: int) -> Optional[UserModel]: ...

    async def get_by_email(self, email: str) -> Optional[UserModel]: ...

    async def create(self, user_data: UserCreate) -> UserModel: ...


class ITokenRepository(Protocol):
    async def create(self, token: str, user_id: int, expires_at: datetime) -> None: ...

    async def get_by_token(self, token: str) -> Optional[RefreshTokenModel]: ...


class ITaskRepository(Protocol):
    async def get_all(
        self,
        user_id: int,
        status: Optional[TaskStatus] = None,
        category_id: Optional[int] = None,
        priority: Optional[TaskPriority] = None,
    ) -> List[TaskModel]: ...

    async def create(
        self, user_id: int, task_data: TaskCreate, tags: list[TaskTagModel] = None
    ) -> TaskModel: ...

    async def get_by_id(self, task_id: int, user_id: int) -> Optional[TaskModel]: ...

    async def update(
        self, task_id: int, user_id: int, task_data: TaskBase
    ) -> TaskModel: ...

    async def delete(self, task_id: int, user_id: int) -> None: ...


class ICategoryRepository(Protocol):
    async def get_all(self, user_id: int) -> List[CategoryModel]: ...

    async def create(
        self, user_id: int, category_data: CategoryCreate
    ) -> CategoryModel: ...


class ISubTaskRepository(Protocol):
    async def create(
        self, user_id: int, task_id: int, subtask_data: SubTaskCreate
    ) -> SubTaskModel: ...

    async def check(self, user_id: int, subtask_id: int) -> SubTaskModel: ...

    async def uncheck(self, user_id: int, subtask_id: int) -> SubTaskModel: ...

    async def delete(self, user_id: int, subtask_id: int) -> None: ...


class ITaskTagRepository(Protocol):
    async def create_or_get(self, tag_name: list[str]) -> list[TaskTagModel]: ...
