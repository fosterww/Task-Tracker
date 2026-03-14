import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from src.models.user import UserModel
from src.services.task_email import _send_welcome_email, _send_daily_summary_email


@pytest.mark.asyncio
async def test_send_welcome_email():
    with patch(
        "src.services.task_email.fast_mail.send_message", new_callable=AsyncMock
    ) as mock_send:
        await _send_welcome_email("test@example.com")
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        message = args[0]
        assert message.subject == "Welcome to Task Tracker"

        recipient = message.recipients[0]
        if hasattr(recipient, "email"):
            assert recipient.email == "test@example.com"
        else:
            assert recipient == "test@example.com"


@pytest.mark.asyncio
async def test_send_daily_summary_email():
    mock_user1 = UserModel(email="user1@example.com")
    mock_user2 = UserModel(email="user2@example.com")

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = [mock_user1, mock_user2]

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_session = AsyncMock()
    mock_session.execute.return_value = mock_result

    mock_session_cm = AsyncMock()
    mock_session_cm.__aenter__.return_value = mock_session
    mock_session_cm.__aexit__.return_value = None

    with (
        patch("src.services.task_email.create_async_engine"),
        patch("src.services.task_email.AsyncSession", return_value=mock_session_cm),
        patch(
            "src.services.task_email._send_welcome_email", new_callable=AsyncMock
        ) as mock_send_welcome,
    ):
        await _send_daily_summary_email()

        mock_session.execute.assert_called_once()

        assert mock_send_welcome.call_count == 2
        mock_send_welcome.assert_any_call("user1@example.com")
        mock_send_welcome.assert_any_call("user2@example.com")
