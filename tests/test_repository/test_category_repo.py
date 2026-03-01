from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.core.exceptions import AppError, DatabaseIntegrityError
from src.models.category import CategoryModel
from src.repository.category_repo import SQLAlchemyCategoryRepository
from src.schemas.category import CategoryCreate


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def category_repo(mock_session):
    return SQLAlchemyCategoryRepository(session=mock_session)


@pytest.mark.asyncio
async def test_get_all_success(category_repo, mock_session):
    mock_category = CategoryModel(id=1, name="Work", owner_id=1)

    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_category]
    mock_session.execute.return_value = mock_result

    categories = await category_repo.get_all(user_id=1)

    assert categories == [mock_category]
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_all_sqlalchemy_error(category_repo, mock_session):
    mock_session.execute.side_effect = SQLAlchemyError("DB error")

    with pytest.raises(AppError, match="Cannot list all tasks"):
        await category_repo.get_all(user_id=1)


@pytest.mark.asyncio
async def test_create_success(category_repo, mock_session):
    category_data = CategoryCreate(name="Personal")

    async def mock_refresh(instance):
        instance.id = 1

    mock_session.refresh = AsyncMock(side_effect=mock_refresh)

    category = await category_repo.create(user_id=1, category_data=category_data)

    assert category.name == "Personal"
    assert category.owner_id == 1
    assert category.id == 1
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_integrity_error(category_repo, mock_session):
    mock_session.commit.side_effect = IntegrityError("error", "params", "orig")

    category_data = CategoryCreate(name="Personal")

    with pytest.raises(
        DatabaseIntegrityError, match="Invalid category_id or data constraints violated"
    ):
        await category_repo.create(user_id=1, category_data=category_data)

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_sqlalchemy_error(category_repo, mock_session):
    mock_session.commit.side_effect = SQLAlchemyError("Generic DB error")

    category_data = CategoryCreate(name="Personal")

    with pytest.raises(AppError, match="Internal database error"):
        await category_repo.create(user_id=1, category_data=category_data)

    mock_session.rollback.assert_awaited_once()
