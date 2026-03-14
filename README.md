# Task Tracker API

An asynchronous RESTful API for managing tasks and categories, built with Python, FastAPI, and PostgreSQL.

## Features

- **User Authentication:** Secure registration and login using JWT (JSON Web Tokens).
- **Task & Category Management:** Create, read, update, and delete tasks/categories with support for subtasks, priorities, and tags.
- **High-Performance Caching:** Integrated Redis caching for categories and tasks using the Decorator pattern to reduce database load.
- **S3-Compatible Storage:** Robust file attachment handling using S3-compatible storage (e.g., MinIO or AWS S3).
- **Background Tasks:** Automated cleanup of old tasks using APScheduler and asynchronous task execution.
- **Dependency Injection:** Powered by [Dishka](https://dishka.readthedocs.io/) for a clean, maintainable, and testable architecture.
- **Database:** Asynchronous PostgreSQL interactions using SQLAlchemy and asyncpg.
- **Migrations:** Database schema migrations handled automatically by Alembic.
- **Validation:** Robust data validation and settings management using Pydantic.
- **Containerization:** Fully containerized setup via Docker and Docker Compose.
- **Kubernetes Ready:** Manifests provided for local deployment via Docker Desktop or Kind.
- **CI/CD:** Automated code quality checks (linting, formatting) and testing via GitHub Actions.

## Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Database:** PostgreSQL
- **Cache:** Redis
- **Storage:** S3-compatible (MinIO/AWS S3)
- **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/) (Async)
- **Migrations:** [Alembic](https://alembic.sqlalchemy.org/)
- **Dependency Injection:** [Dishka](https://github.com/reagento/dishka)
- **Task Scheduling:** APScheduler
- **Package Management:** [uv](https://github.com/astral-sh/uv)
- **Linting & Formatting:** Ruff
- **Testing:** Pytest, pytest-asyncio, httpx

## Prerequisites

- Python 3.12+
- Docker & Docker Desktop (for Kubernetes and DB/Cache services)
- [uv](https://github.com/astral-sh/uv)

## Local Setup & Development

### 1. Clone the repository

```bash
git clone https://github.com/fosterww/Task-Tracker.git
cd task_tracker
```

### 2. Environment Variables

Create a `.env` file in the root directory:

```env
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_NAME=task_tracker_db
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_URL=postgresql+asyncpg://${DATABASE_USER}:${DATABASE_PASSWORD}@${DATABASE_HOST}:${DATABASE_PORT}/${DATABASE_NAME}

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://${REDIS_HOST}:${REDIS_PORT}/0

S3_ENDPOINT=http://localhost:9000
S3_REGION=us-east-1
S3_BUCKET=task-attachments
AWS_ACCESS_KEY_ID=minio
AWS_SECRET_ACCESS_KEY=minio123

SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 3. Install dependencies

```bash
uv sync
```

### 4. Run Services

Start the database, redis, and minio using Docker Compose:

```bash
docker-compose up -d db redis minio
```

### 5. Run Migrations & App

```bash
uv run alembic upgrade head
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## Running with Docker

```bash
docker-compose up -d --build
```

The application will be accessible at `http://localhost:8000`.

## Kubernetes Deployment (Docker Desktop)

1. **Enable Kubernetes** in Docker Desktop Settings.
2. **Build the image**:
   ```bash
   docker build -t task-tracker-app:latest .
   ```
3. **Deploy manifests**:
   ```bash
   kubectl apply -f k8s/
   ```
4. **Access the app**: The LoadBalancer service will expose the API at `http://localhost`.

## Testing

```bash
uv sync --all-extras --dev
uv run pytest
```

To view a detailed test coverage report:

```bash
uv run pytest --cov=src --cov-report=term-missing
```

## Project Structure

```
task_tracker/
├── src/
│   ├── api/          # FastAPI routers (endpoints)
│   ├── core/         # Configurations, IoC container, exceptions
│   ├── models/       # SQLAlchemy models
│   ├── repository/   # Data access layer (with Caching Decorators)
│   ├── schemas/      # Pydantic models
│   └── services/     # Business logic (Cache, Storage, Task services)
├── tests/            # Pytest test suite
├── k8s/              # Kubernetes manifests
├── migrations/       # Alembic migrations
├── docker-compose.yml
├── Dockerfile
└── README.md
```
