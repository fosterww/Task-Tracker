import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_categories(client: AsyncClient):
    email = "get_categories@example.com"
    password = "password123"
    await client.post("/api/auth/register", json={"email": email, "password": password})
    login_response = await client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_category = await client.post(
        "/api/categories/create-category",
        json={"name": "Test Category"},
        headers=headers,
    )
    assert create_category.status_code == 201
    category_id = create_category.json()["id"]

    get_categories = await client.get("/api/categories/get-categories", headers=headers)
    assert get_categories.status_code == 200
    data = get_categories.json()
    assert len(data) > 0
    assert data[0]["id"] == category_id
    assert data[0]["name"] == "Test Category"


@pytest.mark.asyncio
async def test_create_category(client: AsyncClient):
    email = "create_category@example.com"
    password = "password123"
    await client.post("/api/auth/register", json={"email": email, "password": password})
    login_response = await client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_category = await client.post(
        "/api/categories/create-category",
        json={"name": "Test1 Category"},
        headers=headers,
    )
    assert create_category.status_code == 201
    data = create_category.json()
    assert data["name"] == "Test1 Category"
    assert "id" in data
