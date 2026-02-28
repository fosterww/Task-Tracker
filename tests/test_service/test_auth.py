from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.core.exceptions import AuthenticationError, UserAlreadyExistsError
from src.schemas.user import UserCreate
from src.services.auth import login_user, refresh_access_token, register_user


@pytest.mark.asyncio
async def test_register_user_success():
    mock_repo = AsyncMock()
    mock_repo.get_by_email.return_value = None
    mock_repo.create.return_value = AsyncMock(
        id=1, email="test@test.com", username="test"
    )

    new_user = UserCreate(email="test@test.com", password="password1")
    result = await register_user(new_user, mock_repo)

    assert result.id == 1
    assert result.username == "test"
    mock_repo.get_by_email.assert_called_once_with("test@test.com")


@pytest.mark.asyncio
async def test_register_user_already_registered():
    mock_repo = AsyncMock()
    mock_repo.get_by_email.return_value = AsyncMock(
        id=1, email="test@test.com", username="test"
    )

    new_user = UserCreate(email="test@test.com", password="password1")

    with pytest.raises(UserAlreadyExistsError):
        await register_user(new_user, mock_repo)

    mock_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_login_user_success(mocker):
    mock_verify = mocker.patch("src.services.auth.verify_password")
    mock_create_access = mocker.patch("src.services.auth.create_access_token")
    mock_create_refresh = mocker.patch("src.services.auth.create_refresh_token")

    mock_user_repo = AsyncMock()
    mock_token_repo = AsyncMock()

    mock_user = AsyncMock(id=1, hashed_password="hashed")
    mock_user_repo.get_by_email.return_value = mock_user

    mock_verify.return_value = True
    mock_create_access.return_value = "access-token"
    mock_create_refresh.return_value = "refresh-token"

    form_data = OAuth2PasswordRequestForm(
        username="test@test.com", password="password1"
    )

    result = await login_user(form_data, mock_user_repo, mock_token_repo)

    assert result["access_token"] == "access-token"
    assert result["refresh_token"] == "refresh-token"
    mock_token_repo.create.assert_called_once()
    mock_verify.assert_called_once_with("password1", "hashed")


@pytest.mark.asyncio
async def test_login_user_invalid_credential():
    mock_user_repo = AsyncMock()
    mock_token_repo = AsyncMock()

    mock_user_repo.get_by_email.return_value = None

    form_data = OAuth2PasswordRequestForm(
        username="wrong@test.com", password="password1"
    )

    with pytest.raises(AuthenticationError):
        await login_user(form_data, mock_user_repo, mock_token_repo)

    mock_token_repo.create.assert_not_called()


@pytest.mark.asyncio
async def test_login_user_invalid_password(mocker):
    mock_verify = mocker.patch("src.services.auth.verify_password")

    mock_user_repo = AsyncMock()
    mock_token_repo = AsyncMock()

    mock_user = AsyncMock(id=1, hashed_password="hashed")
    mock_user_repo.get_by_email.return_value = mock_user

    mock_verify.return_value = False

    form_data = OAuth2PasswordRequestForm(
        username="test@test.com", password="password1"
    )

    with pytest.raises(AuthenticationError):
        await login_user(form_data, mock_user_repo, mock_token_repo)

    mock_verify.assert_called_once_with("password1", "hashed")


@pytest.mark.asyncio
async def test_refresh_access_token_success(mocker):
    mock_create_access = mocker.patch("src.services.auth.create_access_token")

    mock_user_repo = AsyncMock()
    mock_token_repo = AsyncMock()

    mock_db_token = MagicMock(user_id=1)
    mock_db_token.is_expired.return_value = False
    mock_token_repo.get_by_token.return_value = mock_db_token

    mock_user_repo.get_by_id.return_value = MagicMock(id=1)

    mock_create_access.return_value = "new-access-token"

    result = await refresh_access_token(
        "valid-refresh-token", mock_user_repo, mock_token_repo
    )

    assert result["access_token"] == "new-access-token"
    mock_create_access.assert_called_once_with(data={"sub": "1"})


@pytest.mark.asyncio
async def test_refresh_access_token_expired():
    mock_user_repo = AsyncMock()
    mock_token_repo = AsyncMock()

    mock_db_token = MagicMock()
    mock_db_token.is_expired.return_value = True
    mock_token_repo.get_by_token.return_value = mock_db_token

    mock_user_repo.get_by_id.return_value = MagicMock(id=1)

    with pytest.raises(HTTPException) as exc:
        await refresh_access_token("expired-token", mock_user_repo, mock_token_repo)

    assert exc.value.status_code == 401
    assert "invalid or expired" in exc.value.detail
