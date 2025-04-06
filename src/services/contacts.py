from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas import ContactCreate, ContactUpdate
from src.repository.contacts import ContactRepository
from src.database.models import User

class ContactService:
    def __init__(self, db: AsyncSession):
        self.repository = ContactRepository(db)

    async def get_contacts(self, user: User, skip: int = 0, limit: int = 100):
        return await self.repository.get_contacts(user, skip, limit)

    async def get_contact(self, contact_id: int, user: User):
        return await self.repository.get_contact_by_id(contact_id, user.id)

    async def create_contact(self, body: ContactCreate, user: User):
        return await self.repository.create_contact(body, user.id)

    async def update_contact(self, contact_id: int, body: ContactUpdate, user: User):
        return await self.repository.update_contact(contact_id, body, user.id)

    async def remove_contact(self, contact_id: int, user: User):
        return await self.repository.remove_contact(contact_id, user.id)

    async def search_contacts(self, query: str, user: User):
        return await self.repository.search_contacts(query, user.id)

    async def get_upcoming_birthdays(self, days: int, user: User):
        return await self.repository.upcoming_birthdays(days, user.id)
