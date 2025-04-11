import pytest
from unittest.mock import AsyncMock, patch

from src.services.email import send_email, send_reset_password_email


@pytest.mark.asyncio
@patch("src.services.email.FastMail")
async def test_send_email(mock_fastmail):
    mock_send = AsyncMock()
    mock_fastmail.return_value.send_message = mock_send

    await send_email(
        email="test@example.com",
        username="testuser",
        host="http://localhost:8000",
        token="fake-token"
    )

    mock_fastmail.assert_called_once()
    mock_send.assert_awaited_once()


@pytest.mark.asyncio
@patch("src.services.email.FastMail")
async def test_send_reset_password_email(mock_fastmail):
    mock_send = AsyncMock()
    mock_fastmail.return_value.send_message = mock_send

    await send_reset_password_email(
        email="test@example.com",
        username="testuser",
        host="http://localhost:8000",
        token="fake-token"
    )

    mock_fastmail.assert_called_once()
    mock_send.assert_awaited_once()
