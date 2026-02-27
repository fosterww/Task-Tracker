import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_task_success(client: AsyncClient):
    email = "get_tasks@example.com"
    password = "password123"
    await client.post("/api/auth/register", json={"email": email, "password": password})
    login_response = await client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    task_data = {"title": "Test Task", "description": "This is a test task"}
    create_response = await client.post(
        "/api/tasks/create-task", json=task_data, headers=headers
    )
    assert create_response.status_code == 201

    get_response = await client.get("/api/tasks/", headers=headers)
    assert get_response.status_code == 200

    tasks = get_response.json()
    assert isinstance(tasks, list)
    assert len(tasks) >= 1
    assert any(t["title"] == "Test Task" for t in tasks)


@pytest.mark.asyncio
async def test_update_task_success(client: AsyncClient):
    email = "update_tasks@example.com"
    password = "password123"
    await client.post("/api/auth/register", json={"email": email, "password": password})
    login_response = await client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    task_data = {"title": "Test Task1", "description": "This is a test task"}
    create_response = await client.post(
        "/api/tasks/create-task", json=task_data, headers=headers
    )
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]

    update_data = {"title": "Test Task12"}
    update_resp = await client.patch(
        f"/api/tasks/{task_id}", json=update_data, headers=headers
    )
    assert update_resp.status_code == 200
    data = update_resp.json()
    assert data["id"] == task_id
    assert data["title"] == "Test Task12"


@pytest.mark.asyncio
async def test_delete_task_success(client: AsyncClient):
    email = "delete_tasks@example.com"
    password = "password123"
    await client.post("/api/auth/register", json={"email": email, "password": password})
    login_response = await client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    task_data = {"title": "Test Task3", "description": "This is a test task"}
    create_response = await client.post(
        "/api/tasks/create-task", json=task_data, headers=headers
    )
    assert create_response.status_code == 201

    task_id = create_response.json()["id"]
    delete_resp = await client.delete(f"/api/tasks/{task_id}", headers=headers)
    assert delete_resp.status_code == 204

    get_response = await client.get("/api/tasks/", headers=headers)
    assert get_response.status_code == 200
    data = get_response.json()
    assert data == []


@pytest.mark.asyncio
async def test_create_task_invalid_deadline(client: AsyncClient):
    email = "invalid_deadline@example.com"
    password = "password123"
    await client.post("/api/auth/register", json={"email": email, "password": password})
    login_response = await client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    task_data = {"title": "Test Task", "deadline": "2020-01-01T00:00:00Z"}
    create_response = await client.post(
        "/api/tasks/create-task", json=task_data, headers=headers
    )
    assert create_response.status_code == 422
    assert "Deadline cannot be in the past" in create_response.text


@pytest.mark.asyncio
async def test_update_task_not_found(client: AsyncClient):
    email = "update_not_found@example.com"
    password = "password123"
    await client.post("/api/auth/register", json={"email": email, "password": password})
    login_response = await client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    update_data = {"title": "Test Task12"}
    update_resp = await client.patch(
        "/api/tasks/9999", json=update_data, headers=headers
    )
    assert update_resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_task_not_found(client: AsyncClient):
    email = "delete_not_found@example.com"
    password = "password123"
    await client.post("/api/auth/register", json={"email": email, "password": password})
    login_response = await client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    delete_resp = await client.delete("/api/tasks/9999", headers=headers)
    assert delete_resp.status_code == 404


@pytest.mark.asyncio
async def test_get_tasks_unauthorized(client: AsyncClient):
    get_response = await client.get("/api/tasks/")
    assert get_response.status_code == 401


@pytest.mark.asyncio
async def test_get_task_filters(client: AsyncClient):
    email = "get_tasks_filters@example.com"
    password = "password123"
    await client.post("/api/auth/register", json={"email": email, "password": password})
    login_response = await client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    await client.post(
        "/api/tasks/create-task",
        json={"title": "Task 1", "status": "not_started", "priority": "low"},
        headers=headers,
    )
    await client.post(
        "/api/tasks/create-task",
        json={"title": "Task 2", "status": "pending", "priority": "high"},
        headers=headers,
    )
    get_response = await client.get("/api/tasks/?status=pending", headers=headers)
    assert get_response.status_code == 200
    tasks = get_response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Task 2"

    get_response2 = await client.get("/api/tasks/?priority=low", headers=headers)
    assert get_response2.status_code == 200
    tasks2 = get_response2.json()
    assert len(tasks2) == 1
    assert tasks2[0]["title"] == "Task 1"
