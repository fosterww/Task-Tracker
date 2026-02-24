from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import (
    AppError,
    AuthenticationError,
    TaskNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src.api.auth import router as auth_router
from src.api.category import router as category_router
from src.api.task import router as task_router
from src.core.ioc import AppProvider
from src.core.logger import logger, setup_logging
from src.services.auth import oauth2_scheme
from src.services.task_cleanup import cleanup_old_tasks

container = make_async_container(AppProvider())


async def run_cleanup_task(container: AsyncContainer):
    async with container() as request_container:
        session = await request_container.get(AsyncSession)
        await cleanup_old_tasks(session)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Logger successfuly up")

    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_cleanup_task, "interval", hours=24, args=[container])
    scheduler.start()

    yield

    scheduler.shutdown()


app = FastAPI(title="Task Tracker API", lifespan=lifespan)

setup_dishka(container, app)


@app.exception_handler(AppError)
async def global_exception_handler(request: Request, exc: AppError):
    status_map = {
        UserAlreadyExistsError: 400,
        AuthenticationError: 401,
        UserNotFoundError: 404,
        TaskNotFoundError: 404,
    }

    status_code = status_map.get(type(exc), 400)

    return JSONResponse(status_code=status_code, content={"detail": str(exc)})


app.include_router(auth_router, prefix="/api")
app.include_router(task_router, prefix="/api", dependencies=[Depends(oauth2_scheme)])
app.include_router(
    category_router, prefix="/api", dependencies=[Depends(oauth2_scheme)]
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
