import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.category import CategoryModel
    from src.models.user import UserModel


class TaskStatus(enum.Enum):
    PENDING = "pending"
    NOTSTARTED = "not_started"
    COMPLETED = "completed"


class TaskPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


task_tag_association = Table(
    "task_tag_association",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class TaskModel(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    description: Mapped[str | None] = mapped_column(nullable=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.NOTSTARTED)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    priority: Mapped[TaskPriority] = mapped_column(Enum(TaskPriority), default=TaskPriority.LOW)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=True)

    author: Mapped["UserModel"] = relationship("UserModel", back_populates="tasks")
    category: Mapped["CategoryModel"] = relationship("CategoryModel", back_populates="tasks")
    subtasks: Mapped[list["SubTaskModel"]] = relationship(
        "SubTaskModel",
        back_populates="task",
        cascade="all, delete-orphan"
    )
    tags: Mapped[list["TaskTagModel"]] = relationship(
        "TaskTagModel",
        secondary=task_tag_association,
        back_populates="tasks"
    )


class SubTaskModel(Base):
    __tablename__ = "subtasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    is_done: Mapped[bool] = mapped_column(default=False)

    parent_task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="CASCADE"))

    task: Mapped["TaskModel"] = relationship("TaskModel", back_populates="subtasks")


class TaskTagModel(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, index=True)
    color: Mapped[str | None] = mapped_column(nullable=True)

    tasks: Mapped[list[TaskModel]] = relationship(
        "TaskModel",
        secondary=task_tag_association,
        back_populates="tags"
    )
