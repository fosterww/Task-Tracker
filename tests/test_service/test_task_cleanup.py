from unittest.mock import AsyncMock, MagicMock

import pytest

from src.services.task_cleanup import cleanup_old_tasks


@pytest.mark.asyncio
async def test_task_cleanup_success(mocker, capsys):
    mock_session = AsyncMock()

    mock_result = MagicMock()
    mock_result.rowcount = 10
    mock_session.execute.return_value = mock_result

    mock_delete = mocker.patch("src.services.task_cleanup.delete")
    mock_stmt = MagicMock()

    mock_delete.return_value.where.return_value = mock_stmt

    await cleanup_old_tasks(mock_session)

    captured = capsys.readouterr()

    mock_session.execute.assert_called_once_with(mock_stmt)
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_not_called()
    assert "Cleanup finished. Deleted 10 old tasks." in captured.out


@pytest.mark.asyncio
async def test_cleanup_old_tasks_exception(mocker, capsys):
    mock_session = AsyncMock()

    mock_session.execute.side_effect = Exception("Simulated DB connection lost")

    mock_delete = mocker.patch("src.services.task_cleanup.delete")
    mock_stmt = MagicMock()
    mock_delete.return_value.where.return_value = mock_stmt

    await cleanup_old_tasks(mock_session)

    captured = capsys.readouterr()

    mock_session.execute.assert_called_once_with(mock_stmt)
    mock_session.rollback.assert_called_once()
    mock_session.commit.assert_not_called()
    assert "Cleanup error: Simulated DB connection lost" in captured.out
