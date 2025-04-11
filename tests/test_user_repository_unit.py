import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.repository.users import UserRepository
from src.schemas import UserCreate


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def user_repository(mock_session):
    return UserRepository(mock_session)

@pytest.mark.asyncio
async def test_get_user_by_email(user_repository, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(id=1, username="testuser", email="test@example.com")
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_user_by_email("test@example.com")

    assert user is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_get_user_by_id(user_repository, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(id=1, username="testuser", email="test@example.com")
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_user_by_id(1)

    assert user is not None
    assert user.id == 1


@pytest.mark.asyncio
async def test_get_user_by_username(user_repository, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(id=1, username="testuser", email="test@example.com")
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_user_by_username("testuser")

    assert user is not None
    assert user.username == "testuser"


@pytest.mark.asyncio
async def test_create_user(user_repository, mock_session):
    user_data = UserCreate(username="newuser", email="new@example.com", password="hashedpassword")

    result = await user_repository.create_user(user_data, avatar="http://example.com/avatar.png")

    assert isinstance(result, User)
    assert result.username == "newuser"
    assert result.email == "new@example.com"
    assert result.avatar == "http://example.com/avatar.png"

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)
