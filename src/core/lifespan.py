from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka import AsyncContainer
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logger import logger, setup_logging
from src.services.task_cleanup import cleanup_old_tasks


async def run_cleanup_task(container: AsyncContainer):
    async with container() as request_container:
        session = await request_container.get(AsyncSession)
        await cleanup_old_tasks(session)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    logger.info("Logging successfully up")
    container = app.state.dishka_container

    scheduler = AsyncIOScheduler()
    scheduler.add_job(run_cleanup_task, "interval", hours=24, args=[container])
    scheduler.start()

    try:
        yield
    finally:
        scheduler.shutdown()
