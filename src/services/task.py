from src.core.logger import logger
from src.models.task import TaskModel
from src.repository.base import ITaskRepository, ITaskTagRepository
from src.schemas.task import TaskCreate


class TaskService:
    def __init__(self, task_repo: ITaskRepository, tag_repo: ITaskTagRepository):
        self.task_repo = task_repo
        self.tag_repo = tag_repo

    async def create_task(
        self,
        user_id: int,
        task_data: TaskCreate
    ) -> TaskModel:
        tags = []
        if task_data.tags:
            tags = await self.tag_repo.create_or_get(task_data.tags)

        new_task = await self.task_repo.create(user_id, task_data, tags=tags)

        logger.info(f"User {user_id} created task '{task_data.title}' with {len(tags)} tags")
        return new_task
