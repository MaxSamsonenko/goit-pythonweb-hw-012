"""
Модуль db.py

Цей модуль відповідає за асинхронне керування сесіями бази даних у FastAPI-застосунку.
Він використовує SQLAlchemy для створення асинхронного підключення до бази даних PostgreSQL
і надає контекстний менеджер для безпечного відкриття, використання та закриття сесій.

Компоненти:
- DatabaseSessionManager — клас для керування сесіями бази даних.
- get_db — залежність FastAPI для надання сесії в маршрутах.
"""

import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.conf.config import settings


class DatabaseSessionManager:
    """
    Менеджер сесій бази даних для асинхронної роботи з SQLAlchemy.

    :param url: Рядок підключення до бази даних.
    """

    def __init__(self, url: str):
        self._engine: AsyncEngine = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False,
            autocommit=False,
            bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Контекстний менеджер для надання асинхронної сесії бази даних.

        Забезпечує відкриття сесії, обробку помилок та її закриття після завершення використання.
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(settings.DB_URL)


async def get_db():
    """
    Залежність FastAPI, яка надає сесію бази даних для маршрутів.

    Використовується з Depends(get_db) у функціях FastAPI.
    """
    async with sessionmanager.session() as session:
        yield session
