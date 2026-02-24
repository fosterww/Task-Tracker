from pydantic import BaseModel, ConfigDict


class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    owner_id: int

    model_config = ConfigDict(from_attributes=True)
