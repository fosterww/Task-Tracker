from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.core.exceptions import AppError, UserAlreadyExistsError, UserNotFoundError
from src.models.user import RefreshTokenModel, UserModel
from src.repository.user_repo import SQLAlchemyTokenRepository, SQLAlchemyUserRepository
from src.schemas.user import UserCreate


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def user_repo(mock_session):
    return SQLAlchemyUserRepository(session=mock_session)


@pytest.fixture
def token_repo(mock_session):
    return SQLAlchemyTokenRepository(session=mock_session)


@pytest.mark.asyncio
async def test_get_by_id_success(user_repo, mock_session):
    mock_user = UserModel(id=1, email="test@test.com", username="test")

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_session.execute.return_value = mock_result

    user = await user_repo.get_by_id(1)

    assert user == mock_user
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_not_found(user_repo, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    with pytest.raises(UserNotFoundError):
        await user_repo.get_by_id(999)

    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id_sqlalchemy_error(user_repo, mock_session):
    mock_session.execute.side_effect = SQLAlchemyError("DB error")

    with pytest.raises(AppError, match="Database error while fetching user"):
        await user_repo.get_by_id(1)


@pytest.mark.asyncio
async def test_get_by_email_success(user_repo, mock_session):
    mock_user = UserModel(id=1, email="test@test.com", username="test")

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_session.execute.return_value = mock_result

    user = await user_repo.get_by_email("test@test.com")

    assert user == mock_user
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_email_sqlalchemy_error(user_repo, mock_session):
    mock_session.execute.side_effect = SQLAlchemyError("DB error")

    with pytest.raises(AppError, match="Database error while fetching user"):
        await user_repo.get_by_email("test@test.com")


@pytest.mark.asyncio
async def test_create_user_success(user_repo, mock_session):
    mock_result_exist = MagicMock()
    mock_result_exist.scalar_one_or_none.return_value = None

    mock_user = UserModel(id=1, email="test@test.com", username="test")
    mock_result_create = MagicMock()
    mock_result_create.scalar_one.return_value = mock_user

    mock_session.execute.side_effect = [mock_result_exist, mock_result_create]

    user_data = UserCreate(email="test@test.com", password="password123")

    with patch("src.repository.user_repo.hash_password", return_value="hashed_pw"):
        user = await user_repo.create(user_data)

    assert user == mock_user
    assert mock_session.add.call_count == 1
    mock_session.commit.assert_awaited_once()
    assert mock_session.execute.call_count == 2


@pytest.mark.asyncio
async def test_create_user_already_exists(user_repo, mock_session):
    mock_user = UserModel(id=1, email="test@test.com", username="test")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_user
    mock_session.execute.return_value = mock_result

    user_data = UserCreate(email="test@test.com", password="password123")

    with pytest.raises(UserAlreadyExistsError):
        await user_repo.create(user_data)

    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_awaited()


@pytest.mark.asyncio
async def test_create_user_integrity_error(user_repo, mock_session):
    mock_result_exist = MagicMock()
    mock_result_exist.scalar_one_or_none.return_value = None

    mock_session.execute.return_value = mock_result_exist
    mock_session.commit.side_effect = IntegrityError(
        None, None, Exception("Unique constraint failed")
    )

    user_data = UserCreate(email="test@test.com", password="password123")

    with patch("src.repository.user_repo.hash_password", return_value="hashed_pw"):
        with pytest.raises(AppError, match="Database error while creating user"):
            await user_repo.create(user_data)

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_user_sqlalchemy_error(user_repo, mock_session):
    mock_result_exist = MagicMock()
    mock_result_exist.scalar_one_or_none.return_value = None

    mock_session.execute.return_value = mock_result_exist
    mock_session.commit.side_effect = SQLAlchemyError("Generic DB error")

    user_data = UserCreate(email="test@test.com", password="password123")

    with patch("src.repository.user_repo.hash_password", return_value="hashed_pw"):
        with pytest.raises(AppError, match="Database error while creating user"):
            await user_repo.create(user_data)

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_token_create_success(token_repo, mock_session):
    await token_repo.create("my-token", 1, datetime.now(timezone.utc))

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_token_create_sqlalchemy_error(token_repo, mock_session):
    mock_session.commit.side_effect = SQLAlchemyError("Generic DB error")

    with pytest.raises(AppError, match="Database error while saving token"):
        await token_repo.create("my-token", 1, datetime.now(timezone.utc))

    mock_session.rollback.assert_awaited_once()


@pytest.mark.asyncio
async def test_token_get_by_token_success(token_repo, mock_session):
    mock_token = RefreshTokenModel(id=1, token="my-token", user_id=1)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_token
    mock_session.execute.return_value = mock_result

    token = await token_repo.get_by_token("my-token")

    assert token == mock_token
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_token_get_by_token_sqlalchemy_error(token_repo, mock_session):
    mock_session.execute.side_effect = SQLAlchemyError("DB error")

    with pytest.raises(AppError, match="Database error while verifying token"):
        await token_repo.get_by_token("my-token")
