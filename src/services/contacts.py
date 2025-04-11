"""
Модуль services.contacts

Цей модуль містить сервісний клас ContactService, який реалізує бізнес-логіку для роботи з контактами користувача:
- створення, оновлення, видалення,
- пошук,
- перегляд списку контактів,
- перегляд контактів з днями народження, що наближаються.

Клас використовує репозиторій ContactRepository для взаємодії з базою даних.

Класи:
------
- ContactService: Сервіс для обробки логіки, пов'язаної з контактами користувача.

Методи:
-------
- get_contacts: Отримати список контактів користувача з підтримкою пагінації.
- get_contact: Отримати конкретний контакт за ID.
- create_contact: Створити новий контакт.
- update_contact: Оновити контакт за ID.
- remove_contact: Видалити контакт за ID.
- search_contacts: Знайти контакт(и) за ключовим словом у полях first_name, last_name, email.
- get_upcoming_birthdays: Отримати список контактів, у яких день народження в найближчі N днів.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas import ContactCreate, ContactUpdate
from src.repository.contacts import ContactRepository
from src.database.models import User

class ContactService:
    """
    Сервіс для роботи з контактами користувача.

    :param db: Сесія бази даних.
    :type db: AsyncSession
    """
    def __init__(self, db: AsyncSession):
        self.repository = ContactRepository(db)

    async def get_contacts(self, user: User, skip: int = 0, limit: int = 100):
        """
        Отримати список контактів користувача з пагінацією.

        :param user: Поточний користувач
        :param skip: Кількість контактів, які слід пропустити
        :param limit: Кількість контактів, які слід повернути
        :return: Список контактів
        """
        return await self.repository.get_contacts(user, skip, limit)

    async def get_contact(self, contact_id: int, user: User):
        """
        Отримати контакт за ID.

        :param contact_id: ID контакту
        :param user: Поточний користувач
        :return: Об'єкт контакту або None
        """
        return await self.repository.get_contact_by_id(contact_id, user.id)

    async def create_contact(self, body: ContactCreate, user: User):
        """
        Створити новий контакт.

        :param body: Дані контакту
        :param user: Поточний користувач
        :return: Створений контакт
        """
        return await self.repository.create_contact(body, user.id)

    async def update_contact(self, contact_id: int, body: ContactUpdate, user: User):
        """
        Оновити існуючий контакт.

        :param contact_id: ID контакту
        :param body: Нові дані
        :param user: Поточний користувач
        :return: Оновлений контакт або None
        """
        return await self.repository.update_contact(contact_id, body, user.id)

    async def remove_contact(self, contact_id: int, user: User):
        """
        Видалити контакт.

        :param contact_id: ID контакту
        :param user: Поточний користувач
        :return: Видалений контакт або None
        """
        return await self.repository.remove_contact(contact_id, user.id)

    async def search_contacts(self, query: str, user: User):
        """
        Знайти контакт(и) за ключовим словом у імені, прізвищі або email.

        :param query: Пошукове слово
        :param user: Поточний користувач
        :return: Список знайдених контактів
        """
        return await self.repository.search_contacts(query, user.id)

    async def get_upcoming_birthdays(self, days: int, user: User):
        """
        Отримати контакти, у яких день народження в найближчі `days` днів.

        :param days: Кількість днів наперед
        :param user: Поточний користувач
        :return: Список контактів з днями народження
        """
        return await self.repository.upcoming_birthdays(days, user.id)
