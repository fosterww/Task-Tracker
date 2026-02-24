from datetime import datetime, timedelta, timezone

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.task import TaskModel


async def cleanup_old_tasks(session: AsyncSession):
    treshhold = datetime.now(timezone.utc) - timedelta(days=90)

    try:
        stmt = delete(TaskModel).where(TaskModel.created_at < treshhold)
        result = await session.execute(stmt)
        await session.commit()
        print(f"Cleanup finished. Deleted {result.rowcount} old tasks.")
    except Exception as e:
        await session.rollback()
        print(f"Cleanup error: {e}")
