import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_attachment_success(client: AsyncClient):
    email = "attachment_user@example.com"
    password = "password123"
    await client.post("/api/auth/register", json={"email": email, "password": password})
    login_response = await client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    task_data = {"title": "Task for Attachment"}
    create_response = await client.post(
        "/api/tasks/create-task", json=task_data, headers=headers
    )
    task_id = create_response.json()["id"]

    files = {"file": ("test.png", b"fake image content", "image/png")}
    upload_response = await client.post(
        f"/api/tasks/{task_id}/attachments", files=files, headers=headers
    )

    assert upload_response.status_code == 201
    data = upload_response.json()
    assert data["filename"] == "test.png"
    assert data["content_type"] == "image/png"
    assert "id" in data
    assert data["task_id"] == task_id


@pytest.mark.asyncio
async def test_list_attachment_success(client: AsyncClient):
    email = "list_attachment_user@example.com"
    password = "password123"
    await client.post("/api/auth/register", json={"email": email, "password": password})
    login_response = await client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    task_data = {"title": "Task with Attachments"}
    create_response = await client.post(
        "/api/tasks/create-task", json=task_data, headers=headers
    )
    task_id = create_response.json()["id"]

    for i in range(2):
        files = {"file": (f"test{i}.png", b"content", "image/png")}
        await client.post(
            f"/api/tasks/{task_id}/attachments", files=files, headers=headers
        )

    list_response = await client.get(
        f"/api/tasks/{task_id}/attachments", headers=headers
    )
    assert list_response.status_code == 200
    items = list_response.json()
    assert isinstance(items, list)
    assert len(items) == 2
    assert "test0.png" in [item["filename"] for item in items]
    assert "test1.png" in [item["filename"] for item in items]


@pytest.mark.asyncio
async def test_get_attachment_url_success(client: AsyncClient):
    email = "get_url_user@example.com"
    password = "password123"
    await client.post("/api/auth/register", json={"email": email, "password": password})
    login_response = await client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    task_data = {"title": "Task for URL"}
    create_response = await client.post(
        "/api/tasks/create-task", json=task_data, headers=headers
    )
    task_id = create_response.json()["id"]

    files = {"file": ("test.png", b"content", "image/png")}
    upload_response = await client.post(
        f"/api/tasks/{task_id}/attachments", files=files, headers=headers
    )
    attachment_id = upload_response.json()["id"]

    url_response = await client.get(
        f"/api/tasks/{task_id}/attachments/{attachment_id}/url", headers=headers
    )
    assert url_response.status_code == 200
    assert url_response.json() == "http://mock-url.com"


@pytest.mark.asyncio
async def test_delete_attachment_success(client: AsyncClient):
    email = "delete_attachment_user@example.com"
    password = "password123"
    await client.post("/api/auth/register", json={"email": email, "password": password})
    login_response = await client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    task_data = {"title": "Task to Delete Attachment"}
    create_response = await client.post(
        "/api/tasks/create-task", json=task_data, headers=headers
    )
    task_id = create_response.json()["id"]

    files = {"file": ("test.png", b"content", "image/png")}
    upload_response = await client.post(
        f"/api/tasks/{task_id}/attachments", files=files, headers=headers
    )
    attachment_id = upload_response.json()["id"]

    delete_response = await client.delete(
        f"/api/tasks/{task_id}/attachments/{attachment_id}", headers=headers
    )
    assert delete_response.status_code == 204

    list_response = await client.get(
        f"/api/tasks/{task_id}/attachments", headers=headers
    )
    items = list_response.json()
    assert len(items) == 0
