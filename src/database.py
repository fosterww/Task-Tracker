from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    def to_dict(self) -> dict[str, Any]:
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, Enum):
                value = value.value
            result[column.name] = value
        return result
