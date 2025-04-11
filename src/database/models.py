"""
Модуль models.py

Цей модуль містить SQLAlchemy ORM-моделі для збереження інформації про користувачів і контакти
в базі даних. Визначено таблиці `users` і `contacts`, а також їхні взаємозв'язки.

Класи:
- Base — базовий клас для всіх моделей, створений за допомогою SQLAlchemy DeclarativeBase.
- User — модель користувача, яка зберігає дані про ім’я, email, пароль, аватар та статус підтвердження.
- Contact — модель контакту, пов’язана з користувачем, що зберігає інформацію про контакти користувача.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, func, Date, Boolean, DateTime
from sqlalchemy.orm import relationship, mapped_column, Mapped, DeclarativeBase
from sqlalchemy.sql.schema import ForeignKey

from sqlalchemy import Enum as SqlEnum
import enum


class Base(DeclarativeBase):
    """
    Базовий клас для моделей SQLAlchemy.
    Всі ORM-моделі мають наслідувати цей клас.
    """
    pass

class Role(enum.Enum):
    admin = "admin"
    user = "user"

class Contact(Base):
    """
    ORM-модель для представлення контактів користувача.

    Атрибути:
    - id: Унікальний ідентифікатор контакту.
    - first_name: Ім’я контакту.
    - last_name: Прізвище контакту.
    - email: Електронна пошта контакту.
    - phone: Номер телефону.
    - birthday: Дата народження.
    - extra_info: Додаткова інформація.
    - user_id: Ідентифікатор користувача, якому належить контакт.
    - user: Об'єкт користувача, пов’язаний із цим контактом.
    """

    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    birthday: Mapped[datetime.date] = mapped_column(Date)
    extra_info: Mapped[str] = mapped_column(String(250), nullable=True)
    user_id = Column(
        "user_id", ForeignKey("users.id", ondelete="CASCADE"), default=None
    )
    user = relationship("User", backref="notes")


class User(Base):
    """
    ORM-модель для представлення користувачів.

    Атрибути:
    - id: Унікальний ідентифікатор користувача.
    - username: Унікальне ім’я користувача.
    - email: Унікальна адреса електронної пошти.
    - hashed_password: Хешований пароль.
    - created_at: Дата та час створення облікового запису.
    - avatar: URL аватара користувача.
    - confirmed: Статус підтвердження електронної пошти.
    """

    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    role = Column(SqlEnum(Role), default=Role.user)
