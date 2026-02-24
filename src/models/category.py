from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class CategoryModel(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    owner: Mapped["UserModel"] = relationship("UserModel", back_populates="categories")
    tasks: Mapped[list["TaskModel"]] = relationship("TaskModel", back_populates="category")
