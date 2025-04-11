import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.repository.contacts import ContactRepository
from src.schemas import ContactCreate


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def contact_repository(mock_session):
    return ContactRepository(mock_session)

@pytest.fixture
def user():
    return User(id=1, username="testuser", email="test@example.com")


@pytest.mark.asyncio
async def test_get_contacts(contact_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Contact(id=1, first_name="Alice", last_name="Smith", user_id=user.id)
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    contacts = await contact_repository.get_contacts(user_id=user.id, skip=0, limit=10)

    assert len(contacts) == 1
    assert contacts[0].first_name == "Alice"


@pytest.mark.asyncio
async def test_get_contact_by_id(contact_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Contact(
        id=1, first_name="Alice", last_name="Smith", user_id=user.id
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    contact = await contact_repository.get_contact_by_id(contact_id=1, user_id=user.id)

    assert contact is not None
    assert contact.id == 1
    assert contact.first_name == "Alice"


@pytest.mark.asyncio
async def test_create_contact(contact_repository, mock_session, user):
    contact_data = ContactCreate(
        first_name="Bob", last_name="Johnson", email="bob@example.com", phone="123-456-7890"
    )

    result = await contact_repository.create_contact(body=contact_data, user_id=user.id)

    assert isinstance(result, Contact)
    assert result.first_name == "Bob"
    assert result.email == "bob@example.com"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_remove_contact(contact_repository, mock_session, user):
    existing_contact = Contact(id=1, first_name="Delete", last_name="Me", user_id=user.id)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contact_repository.remove_contact(contact_id=1, user_id=user.id)

    assert result is not None
    assert result.first_name == "Delete"
    mock_session.delete.assert_awaited_once_with(existing_contact)
    mock_session.commit.assert_awaited_once()
