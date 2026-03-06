from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginationParams(BaseModel):
    skip: int = 0
    offset: int = 0
    limit: int = 10
    search: str | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool

    @classmethod
    def create(cls, items: List[T], total: int, offset: int, limit: int):
        return cls(
            items=items,
            total=total,
            page=(offset // limit) + 1,
            page_size=limit,
            total_pages=(total + limit - 1) // limit if total > 0 else 1,
            has_next=(offset + limit) < total,
            has_previous=offset > 0,
        )
