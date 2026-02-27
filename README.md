# Task Tracker API

An asynchronous RESTful API for managing tasks and categories, built with Python, FastAPI, and PostgreSQL.

## Features

- **User Authentication:** Secure registration and login using JWT (JSON Web Tokens).
- **Task Management:** Create, read, update, and delete tasks. Support for subtasks, priorities, and tags.
- **Category Management:** Organize tasks into custom categories.
- **Background Tasks:** Automated cleanup of old tasks using APScheduler.
- **Dependency Injection:** Powered by [Dishka](https://dishka.readthedocs.io/) for a clean, maintainable, and testable architecture.
- **Database:** Asynchronous PostgreSQL interactions using SQLAlchemy and asyncpg.
- **Migrations:** Database schema migrations handled automatically by Alembic.
- **Validation:** Robust data validation and settings management using Pydantic.
- **Containerization:** Fully containerized setup via Docker and Docker Compose.
- **CI/CD:** Automated code quality checks (linting, formatting) and testing via GitHub Actions.

## Tech Stack

- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Database:** PostgreSQL
- **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/) (Async)
- **Migrations:** [Alembic](https://alembic.sqlalchemy.org/)
- **Dependency Injection:** [Dishka](https://github.com/reagento/dishka)
- **Task Scheduling:** APScheduler
- **Package Management:** [uv](https://github.com/astral-sh/uv)
- **Linting & Formatting:** Ruff
- **Testing:** Pytest, pytest-asyncio, httpx

## Prerequisites

- Python 3.12+
- Docker & Docker Compose
- PostgreSQL (if running locally without Docker)
- [uv](https://github.com/astral-sh/uv) (for fast Python package and dependency management)

## Local Setup & Development

### 1. Clone the repository

```bash
git clone https://github.com/fosterww/Task-Tracker.git
cd task_tracker
```

### 2. Environment Variables

Create a `.env` file in the root directory and configure the necessary environment variables:

```env
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_NAME=task_tracker_db
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_URL=postgresql+asyncpg://${DATABASE_USER}:${DATABASE_PASSWORD}@${DATABASE_HOST}:${DATABASE_PORT}/${DATABASE_NAME}

SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

### 3. Install dependencies

This project utilizes `uv` to manage dependencies efficiently.

```bash
# Create a virtual environment and sync dependencies
uv sync
```

### 4. Run Database Migrations

Ensure your PostgreSQL instance is running. Then, apply the Alembic database migrations to create the required tables:

```bash
uv run alembic upgrade head
```

### 5. Run the Application

Start the FastAPI development server:

```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`.
You can access the auto-generated, interactive API documentation (Swagger UI) at `http://localhost:8000/docs`.

## Running with Docker

You can easily start the application and its database together using Docker Compose. Make sure your `.env` file is present.

```bash
# This will build the API image and start the DB and App services in the background
docker-compose up -d --build
```

The application will be accessible at `http://localhost:8000` just like the local setup.

## Testing

Tests are written using `pytest` and `pytest-asyncio`. To execute the test suite:

```bash
# Ensure development dependencies are installed
uv sync --all-extras --dev

# Run tests
uv run pytest
```

To view a detailed test coverage report:

```bash
uv run pytest --cov=src --cov-report=term-missing
```

## Linting and Formatting

The project uses [Ruff](https://docs.astral.sh/ruff/) for blazing-fast Python linting and code formatting.

```bash
# Check for linting errors
uvx ruff check .

# Format the codebase
uvx ruff format .
```

## Project Structure

```
task_tracker/
├── src/
│   ├── api/          # FastAPI routers (endpoints)
│   ├── core/         # Core application configurations, IoC container, exceptions
│   ├── models/       # SQLAlchemy database models
│   ├── repository/   # Data access layer (Database operations)
│   ├── schemas/      # Pydantic models (data validation and serialization)
│   └── services/     # Core business logic layer
├── tests/            # Pytest test suite
├── migrations/       # Alembic database migration scripts
├── alembic.ini       # Alembic configuration
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml    # Project metadata and dependencies
└── README.md
```
