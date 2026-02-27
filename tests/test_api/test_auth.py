import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient):
    payload = {"email": "register@example.com", "password": "string1234"}

    response = await client.post("/api/auth/register", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert data["username"] == "register"
    assert data["tasks"] == []


@pytest.mark.asyncio
async def test_register_user_duplicate(client: AsyncClient):
    payload = {"email": "register1@example.com", "password": "string1234"}

    first = await client.post("/api/auth/register", json=payload)
    assert first.status_code == 200

    second = await client.post("/api/auth/register", json=payload)
    assert second.status_code == 400
    assert second.json()["detail"] == "User with this email already exists"


@pytest.mark.asyncio
async def test_register_invalid_email_returns_422(client):
    payload = {"email": "not-an-email", "password": "string"}

    response = await client.post("/api/auth/register", json=payload)

    assert response.status_code == 422
    details = response.json()["detail"]
    assert any(item["loc"][-1] == "email" for item in details)


@pytest.mark.asyncio
async def test_login_user_success(client: AsyncClient):
    email = "login@example.com"
    password = "string1234"

    register = await client.post(
        "/api/auth/register", json={"email": email, "password": password}
    )
    assert register.status_code == 200

    login = await client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    data = login.json()
    assert login.status_code == 200
    assert data["access_token"]
    assert data["refresh_token"]


@pytest.mark.asyncio
async def test_login_user_incorrect_email(client: AsyncClient):
    email = "login1@example.com"
    password = "string1234"

    register = await client.post(
        "/api/auth/register", json={"email": email, "password": password}
    )
    assert register.status_code == 200

    login = await client.post(
        "/api/auth/login",
        data={"username": "user1@example.com", "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login.status_code == 401
    assert login.json()["detail"] == "Incorrect email or password"


@pytest.mark.asyncio
async def test_login_user_incorrect_password(client: AsyncClient):
    email = "login2@example.com"
    password = "string1234"

    register = await client.post(
        "/api/auth/register", json={"email": email, "password": password}
    )
    assert register.status_code == 200

    login = await client.post(
        "/api/auth/login",
        data={"username": "email", "password": "string12"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login.status_code == 401
    assert login.json()["detail"] == "Incorrect email or password"


@pytest.mark.asyncio
async def test_refresh_token_success(client: AsyncClient):
    email = "refresh@example.com"
    password = "string1234"

    await client.post("/api/auth/register", json={"email": email, "password": password})

    login = await client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    refresh_token = login.json()["refresh_token"]

    refresh = await client.post(f"/api/auth/refresh?refresh_token={refresh_token}")

    assert refresh.status_code == 200
    data = refresh.json()
    assert data["access_token"]
    assert "refresh_token" not in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_refresh_token_invalid(client: AsyncClient):
    refresh = await client.post("/api/auth/refresh?refresh_token=invalid_token")
    assert refresh.status_code == 401
    assert refresh.json()["detail"] == "Refresh token invalid or expired"
