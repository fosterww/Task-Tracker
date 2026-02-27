import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_subtask_success(client: AsyncClient):
    email = "create_subtask@example.com"
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
    task_id = create_response.json()["id"]
    assert create_response.status_code == 201

    subtask_data = {"title": "Test SubTask"}
    create_subtask_resp = await client.post(
        f"/api/tasks/{task_id}/subtasks", json=subtask_data, headers=headers
    )
    assert create_subtask_resp.status_code == 200
    data = create_subtask_resp.json()
    assert data["parent_task_id"] == task_id


@pytest.mark.asyncio
async def test_check_subtask_success(client: AsyncClient):
    email = "check_subtask@example.com"
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

    task_data = {"title": "Test Task4", "description": "This is a test task"}
    create_response = await client.post(
        "/api/tasks/create-task", json=task_data, headers=headers
    )
    task_id = create_response.json()["id"]
    assert create_response.status_code == 201

    subtask_data = {"title": "Test SubTask1", "is_done": False}
    create_subtask_resp = await client.post(
        f"/api/tasks/{task_id}/subtasks", json=subtask_data, headers=headers
    )
    assert create_subtask_resp.status_code == 200
    subtask_id = create_subtask_resp.json()["id"]

    check_subtask = await client.patch(
        f"/api/tasks/subtasks/{subtask_id}/check", headers=headers
    )
    assert check_subtask.status_code == 200
    data = check_subtask.json()
    assert data["id"] == subtask_id
    assert data["parent_task_id"] == task_id
    assert data["is_done"] is True


@pytest.mark.asyncio
async def test_uncheck_subtask_success(client: AsyncClient):
    email = "uncheck_subtask@example.com"
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

    task_data = {"title": "Test Task4", "description": "This is a test task"}
    create_response = await client.post(
        "/api/tasks/create-task", json=task_data, headers=headers
    )
    task_id = create_response.json()["id"]
    assert create_response.status_code == 201

    subtask_data = {"title": "Test SubTask1", "is_done": True}
    create_subtask_resp = await client.post(
        f"/api/tasks/{task_id}/subtasks", json=subtask_data, headers=headers
    )
    assert create_subtask_resp.status_code == 200
    subtask_id = create_subtask_resp.json()["id"]

    check_subtask = await client.patch(
        f"/api/tasks/subtasks/{subtask_id}/uncheck", headers=headers
    )
    assert check_subtask.status_code == 200
    data = check_subtask.json()
    assert data["id"] == subtask_id
    assert data["parent_task_id"] == task_id
    assert data["is_done"] is False


@pytest.mark.asyncio
async def test_delete_subtask_success(client: AsyncClient):
    email = "delete_subtask@example.com"
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

    task_data = {"title": "Test Task5", "description": "This is a test task"}
    create_response = await client.post(
        "/api/tasks/create-task", json=task_data, headers=headers
    )
    task_id = create_response.json()["id"]
    assert create_response.status_code == 201

    subtask_data = {"title": "Test SubTask1"}
    create_subtask_resp = await client.post(
        f"/api/tasks/{task_id}/subtasks", json=subtask_data, headers=headers
    )
    assert create_subtask_resp.status_code == 200
    subtask_id = create_subtask_resp.json()["id"]

    delete_subtask = await client.delete(
        f"/api/tasks/subtasks/{subtask_id}", headers=headers
    )
    assert delete_subtask.status_code == 204


@pytest.mark.asyncio
async def test_create_subtask_not_found(client: AsyncClient):
    email = "create_subtask_not_found@example.com"
    password = "password123"
    await client.post("/api/auth/register", json={"email": email, "password": password})
    login_response = await client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    subtask_data = {"title": "Test SubTask Not Found"}
    create_subtask_resp = await client.post(
        "/api/tasks/999999/subtasks", json=subtask_data, headers=headers
    )
    assert create_subtask_resp.status_code == 404
    assert create_subtask_resp.json()["detail"] == "Task not found or access denied"


@pytest.mark.asyncio
async def test_check_subtask_not_found(client: AsyncClient):
    email = "check_subtask_not_found@example.com"
    password = "password123"
    await client.post("/api/auth/register", json={"email": email, "password": password})
    login_response = await client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    check_subtask = await client.patch(
        "/api/tasks/subtasks/999999/check", headers=headers
    )
    assert check_subtask.status_code == 404
    assert check_subtask.json()["detail"] == "Task not found or access denied"


@pytest.mark.asyncio
async def test_uncheck_subtask_not_found(client: AsyncClient):
    email = "uncheck_subtask_not_found@example.com"
    password = "password123"
    await client.post("/api/auth/register", json={"email": email, "password": password})
    login_response = await client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    uncheck_subtask = await client.patch(
        "/api/tasks/subtasks/999999/uncheck", headers=headers
    )
    assert uncheck_subtask.status_code == 404
    assert uncheck_subtask.json()["detail"] == "Task not found or access denied"


@pytest.mark.asyncio
async def test_delete_subtask_not_found(client: AsyncClient):
    email = "delete_subtask_not_found@example.com"
    password = "password123"
    await client.post("/api/auth/register", json={"email": email, "password": password})
    login_response = await client.post(
        "/api/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    delete_subtask = await client.delete("/api/tasks/subtasks/999999", headers=headers)
    assert delete_subtask.status_code == 404
    assert delete_subtask.json()["detail"] == "Task not found or access denied"
