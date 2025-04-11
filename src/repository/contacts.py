"""
Модуль contact.py

Цей модуль містить клас ContactRepository, який реалізує доступ до бази даних
для об'єктів контактів користувача (Contact) з використанням SQLAlchemy AsyncSession.

Клас:
- ContactRepository — реалізує CRUD-операції, пошук і отримання майбутніх днів народжень.
"""

from typing import List
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact
from src.schemas import ContactCreate, ContactUpdate


class ContactRepository:
    """
    Репозиторій для управління контактами користувача.

    Методи:
    - get_contacts: Отримати список контактів користувача з пагінацією.
    - get_contact_by_id: Отримати контакт за його ID, якщо він належить користувачу.
    - create_contact: Створити новий контакт для користувача.
    - update_contact: Оновити дані існуючого контакту.
    - remove_contact: Видалити контакт користувача.
    - search_contacts: Пошук контактів за іменем, прізвищем або email.
    - upcoming_birthdays: Отримати список контактів з днями народження у найближчі N днів.
    """

    def __init__(self, session: AsyncSession):
        """
        Ініціалізує ContactRepository з переданою асинхронною сесією бази даних.

        :param session: Об'єкт асинхронної сесії SQLAlchemy.
        """
        self.db = session

    async def get_contacts(self, user_id: int, skip: int, limit: int) -> List[Contact]:
        """
        Отримати всі контакти користувача з можливістю пагінації.

        :param user_id: Ідентифікатор користувача.
        :param skip: Кількість записів для пропуску.
        :param limit: Максимальна кількість записів.
        :return: Список контактів.
        """
        stmt = select(Contact).where(Contact.user_id == user_id).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_contact_by_id(self, contact_id: int, user_id: int) -> Contact | None:
        """
        Отримати конкретний контакт за ID, якщо він належить користувачу.

        :param contact_id: Ідентифікатор контакту.
        :param user_id: Ідентифікатор користувача.
        :return: Об'єкт Contact або None.
        """
        stmt = select(Contact).where(Contact.id == contact_id, Contact.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_contact(self, body: ContactCreate, user_id: int) -> Contact:
        """
        Створити новий контакт для користувача.

        :param body: Дані для створення контакту.
        :param user_id: Ідентифікатор користувача.
        :return: Створений об'єкт Contact.
        """
        contact = Contact(**body.model_dump(), user_id=user_id)
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(self, contact_id: int, body: ContactUpdate, user_id: int) -> Contact | None:
        """
        Оновити контакт користувача.

        :param contact_id: Ідентифікатор контакту.
        :param body: Дані для оновлення.
        :param user_id: Ідентифікатор користувача.
        :return: Оновлений об'єкт Contact або None.
        """
        contact = await self.get_contact_by_id(contact_id, user_id)
        if contact:
            for key, value in body.model_dump(exclude_unset=True).items():
                setattr(contact, key, value)
            await self.db.commit()
            await self.db.refresh(contact)
        return contact

    async def remove_contact(self, contact_id: int, user_id: int) -> Contact | None:
        """
        Видалити контакт користувача.

        :param contact_id: Ідентифікатор контакту.
        :param user_id: Ідентифікатор користувача.
        :return: Видалений об'єкт Contact або None.
        """
        contact = await self.get_contact_by_id(contact_id, user_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
        return contact

    async def search_contacts(self, query: str, user_id: int) -> List[Contact]:
        """
        Пошук контактів користувача за іменем, прізвищем або електронною поштою.

        :param query: Рядок пошуку.
        :param user_id: Ідентифікатор користувача.
        :return: Список знайдених контактів.
        """
        stmt = select(Contact).filter(
            Contact.user_id == user_id,
            (Contact.first_name.ilike(f"%{query}%")) |
            (Contact.last_name.ilike(f"%{query}%")) |
            (Contact.email.ilike(f"%{query}%"))
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def upcoming_birthdays(self, days: int, user_id: int) -> List[Contact]:
        """
        Отримати список контактів, дні народження яких відбудуться протягом вказаної кількості днів.

        :param days: Кількість днів вперед.
        :param user_id: Ідентифікатор користувача.
        :return: Список контактів.
        """
        today = datetime.today().date()
        end_date = today + timedelta(days=days)
        stmt = select(Contact).filter(
            Contact.user_id == user_id,
            Contact.birthday >= today,
            Contact.birthday <= end_date
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
