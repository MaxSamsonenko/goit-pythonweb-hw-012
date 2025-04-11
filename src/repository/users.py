"""
Модуль user.py

Цей модуль містить клас UserRepository, який реалізує операції доступу до бази даних 
для об'єктів користувачів (User), з використанням асинхронної сесії SQLAlchemy.

Клас:
- UserRepository — CRUD-операції для моделі User.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserCreate


class UserRepository:
    """
    Репозиторій для управління користувачами.

    Методи:
    - get_user_by_id: Отримати користувача за його унікальним ID.
    - get_user_by_username: Отримати користувача за його username.
    - get_user_by_email: Отримати користувача за email.
    - create_user: Створити нового користувача з можливим аватаром.
    """

    def __init__(self, session: AsyncSession):
        """
        Ініціалізація репозиторію з переданою асинхронною сесією бази даних.

        :param session: Об'єкт асинхронної сесії SQLAlchemy.
        """
        self.db = session

    async def get_user_by_id(self, user_id: int) -> User | None:
        """
        Отримати користувача за його ID.

        :param user_id: Ідентифікатор користувача.
        :return: Об'єкт User або None, якщо користувач не знайдений.
        """
        stmt = select(User).filter_by(id=user_id)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Отримати користувача за username.

        :param username: Ім'я користувача.
        :return: Об'єкт User або None.
        """
        stmt = select(User).filter_by(username=username)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Отримати користувача за електронною поштою.

        :param email: Email користувача.
        :return: Об'єкт User або None.
        """
        stmt = select(User).filter_by(email=email)
        user = await self.db.execute(stmt)
        return user.scalar_one_or_none()

    async def create_user(self, body: UserCreate, avatar: str = None) -> User:
        """
        Створити нового користувача на основі даних зі схеми.

        :param body: Об'єкт UserCreate з даними для створення користувача.
        :param avatar: URL аватара користувача (необов'язково).
        :return: Створений об'єкт User.
        """
        user = User(
            **body.model_dump(exclude_unset=True, exclude={"password"}),
            hashed_password=body.password,
            avatar=avatar
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
