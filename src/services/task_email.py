import asyncio

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from src.core.celery import celery_app
from src.core.config import dbsettings, srcsettings
from src.core.logger import logger
from src.models.category import CategoryModel
from src.models.task import TaskModel
from src.models.user import UserModel

conf = ConnectionConfig(
    MAIL_USERNAME=srcsettings.MAIL_USERNAME,
    MAIL_PASSWORD=srcsettings.MAIL_PASSWORD,
    MAIL_FROM=srcsettings.MAIL_FROM,
    MAIL_PORT=srcsettings.MAIL_PORT,
    MAIL_SERVER=srcsettings.MAIL_SERVER,
    MAIL_STARTTLS=srcsettings.MAIL_STARTTLS,
    MAIL_SSL_TLS=srcsettings.MAIL_SSL_TLS,
    USE_CREDENTIALS=srcsettings.USE_CREDENTIALS,
    VALIDATE_CERTS=srcsettings.VALIDATE_CERTS,
)

fast_mail = FastMail(conf)


async def _send_welcome_email(email_to: str):
    html_content = """
    <html>
        <body>
            <h2>Welcome to Task Tracker!</h2>
            <p>We are excited to have you on board. Start creating tasks and organizing your life today!</p>
        </body>
    </html>
    """

    message = MessageSchema(
        subject="Welcome to Task Tracker",
        recipients=[email_to],
        body=html_content,
        subtype=MessageType.html,
    )

    try:
        await fast_mail.send_message(message)
        logger.info(f"Welcome email sent to {email_to}")
    except Exception as e:
        logger.error(f"Failed to send welcome email to {email_to}: {e}")


@celery_app.task
def send_welcome_email_task(email_to: str):
    asyncio.run(_send_welcome_email(email_to))


async def _send_daily_summary_email():
    engine = create_async_engine(dbsettings.DATABASE_URL)
    async with AsyncSession(engine) as db:
        query = select(UserModel).join(TaskModel).join(CategoryModel)
        result = await db.execute(query)
        users = result.scalars().all()
        for user in users:
            await _send_welcome_email(user.email)
    logger.info("Daily summary email task executed.")


@celery_app.task
def send_daily_summary_email():
    asyncio.run(_send_daily_summary_email())
