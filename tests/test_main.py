import json
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI, Request

from src.core.exceptions import (
    AppError,
    AuthenticationError,
    TaskNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src.main import container, global_exception_handler, lifespan, run_cleanup_task


@pytest.mark.asyncio
async def test_lifespan_startup_shutdown(mocker):
    mock_setup_logging = mocker.patch("src.main.setup_logging")
    mock_logger = mocker.patch("src.main.logger")
    mock_scheduler = mocker.patch("src.main.AsyncIOScheduler")
    app = FastAPI()

    mock_scheduler_instance = MagicMock()
    mock_scheduler.return_value = mock_scheduler_instance

    async with lifespan(app):
        mock_setup_logging.assert_called_once()
        mock_logger.info.assert_called_once_with("Logger successfully up")

        mock_scheduler.assert_called_once()

        mock_scheduler_instance.add_job.assert_called_once_with(
            run_cleanup_task, "interval", hours=24, args=[container]
        )
        mock_scheduler_instance.start.assert_called_once()

        mock_scheduler_instance.shutdown.assert_not_called()

    mock_scheduler_instance.shutdown.assert_called_once()


@pytest.mark.asycnio
@pytest.mark.parametrize(
    "exception_class, expected_status_code",
    [
        (UserAlreadyExistsError, 400),
        (AuthenticationError, 401),
        (UserNotFoundError, 404),
        (TaskNotFoundError, 404),
        (AppError, 400),
    ],
)
async def test_global_exception_handler(exception_class, expected_status_code):
    mock_request = Request(scope={"type": "http"})

    exc = exception_class()

    response = await global_exception_handler(mock_request, exc)

    assert response.status_code == expected_status_code

    response_body = json.loads(response.body.decode("utf-8"))

    assert response_body == {"detail": str(exc)}
