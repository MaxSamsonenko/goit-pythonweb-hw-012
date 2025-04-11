"""
Модуль services.users

Цей модуль реалізує сервісний клас UserService для роботи з користувачами.
Він взаємодіє з репозиторієм UserRepository і забезпечує логіку створення та отримання користувачів.

Класи:
------
- UserService: Обробляє логіку створення, пошуку та підтвердження користувачів.

Методи:
-------
- create_user: Створює нового користувача з автоматично згенерованим аватаром через Gravatar.
- get_user_by_id: Повертає користувача за його ID.
- get_user_by_username: Повертає користувача за ім’ям.
- get_user_by_email: Повертає користувача за email.
- create_user_from_data: Створює підтвердженого користувача з даних, отриманих після верифікації email.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from libgravatar import Gravatar

from src.repository.users import UserRepository
from src.schemas import UserCreate
from src.database.models import User

class UserService:
    """
    Сервіс для роботи з користувачами.

    :param db: Асинхронна сесія бази даних
    :type db: AsyncSession
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = UserRepository(db)

    async def create_user(self, body: UserCreate):
        """
        Створює нового користувача. Автоматично додає аватар з Gravatar, якщо доступний.

        :param body: Дані для створення користувача
        :type body: UserCreate
        :return: Об’єкт створеного користувача
        :rtype: User
        """
        avatar = None
        try:
            g = Gravatar(body.email)
            avatar = g.get_image()
        except Exception as e:
            print(e)

        return await self.repository.create_user(body, avatar)

    async def get_user_by_id(self, user_id: int):
        """
        Отримує користувача за ID.

        :param user_id: Ідентифікатор користувача
        :type user_id: int
        :return: Об’єкт користувача або None
        :rtype: User | None
        """
        return await self.repository.get_user_by_id(user_id)

    async def get_user_by_username(self, username: str):
        """
        Отримує користувача за ім'ям.

        :param username: Ім’я користувача
        :type username: str
        :return: Об’єкт користувача або None
        :rtype: User | None
        """
        return await self.repository.get_user_by_username(username)

    async def get_user_by_email(self, email: str):
        """
        Отримує користувача за електронною адресою.

        :param email: Email користувача
        :type email: str
        :return: Об’єкт користувача або None
        :rtype: User | None
        """
        return await self.repository.get_user_by_email(email)
    
    async def create_user_from_data(self, email: str, username: str, password: str):
        """
        Створює нового підтвердженого користувача після переходу за посиланням з email.

        :param email: Email користувача
        :param username: Ім’я користувача
        :param password: Хешований пароль
        :return: Об’єкт створеного користувача
        :rtype: User
        """
        user = User(email=email, username=username, hashed_password=password, confirmed=True)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
