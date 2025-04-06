from typing import List
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.schemas import ContactCreate, ContactUpdate

class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_contacts(self, user_id: int, skip: int, limit: int) -> List[Contact]:
        print(f"Looking for contacts with user_id={user_id}")
        stmt = select(Contact).where(Contact.user_id == user_id).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        contacts = result.scalars().all()
        print("Found contacts:", contacts)
        return contacts

    async def get_contact_by_id(self, contact_id: int, user_id: int) -> Contact | None:
        stmt = select(Contact).where(Contact.id == contact_id, Contact.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_contact(self, body: ContactCreate, user_id: int) -> Contact:
        contact = Contact(**body.model_dump(), user_id=user_id)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(self, contact_id: int, body: ContactUpdate, user_id: int) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id, user_id)
        if contact:
            for key, value in body.model_dump(exclude_unset=True).items():
                setattr(contact, key, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int, user_id: int) -> Contact | None:
        contact = await self.get_contact_by_id(contact_id, user_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def search_contacts(self, query: str, user_id: int) -> List[Contact]:
        stmt = select(Contact).filter(
            Contact.user_id == user_id,
            (Contact.first_name.ilike(f"%{query}%")) |
            (Contact.last_name.ilike(f"%{query}%")) |
            (Contact.email.ilike(f"%{query}%"))
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def upcoming_birthdays(self, days: int, user_id: int) -> List[Contact]:
        today = datetime.today().date()
        end_date = today + timedelta(days=days)
        stmt = select(Contact).filter(
            Contact.user_id == user_id,
            Contact.birthday >= today,
            Contact.birthday <= end_date
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
