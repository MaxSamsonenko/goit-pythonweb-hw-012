"""
Модуль schemas

Цей модуль містить Pydantic-схеми для валідації вхідних даних та формування відповідей у застосунку FastAPI.

Схеми:
------

Контакти:
- ContactBase: Базова модель контакту.
- ContactCreate: Модель для створення нового контакту.
- ContactUpdate: Модель для оновлення існуючого контакту.
- ContactResponse: Модель відповіді, яка включає ID контакту.

Користувачі:
- User: Схема відповіді з інформацією про користувача.
- UserCreate: Схема створення нового користувача.
- UserLogin: Схема логіну користувача.
- Token: Схема JWT токену.
- RequestEmail: Схема запиту для повторного надсилання email.
"""

from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict

# -------------------- CONTACTS --------------------

class ContactBase(BaseModel):
    """
    Базова схема контакту.
    """
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: EmailStr
    phone: str = Field(max_length=20)
    birthday: Optional[date] = None
    extra_info: Optional[str] = Field(default=None, max_length=250)


class ContactCreate(ContactBase):
    """
    Схема для створення нового контакту. Наслідується від ContactBase.
    """
    pass


class ContactUpdate(ContactBase):
    """
    Схема для оновлення існуючого контакту. Наслідується від ContactBase.
    """
    pass


class ContactResponse(ContactBase):
    """
    Схема відповіді, що включає ID контакту.

    :param id: Унікальний ідентифікатор контакту
    """
    id: int
    model_config = ConfigDict(from_attributes=True)


# -------------------- USERS --------------------

class User(BaseModel):
    """
    Схема відповіді з інформацією про користувача.

    :param id: Ідентифікатор користувача
    :param username: Ім’я користувача
    :param email: Електронна пошта
    :param avatar: URL до аватара користувача
    """
    id: int
    username: str
    email: str
    avatar: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """
    Схема для створення нового користувача.

    :param username: Ім’я користувача (мінімум 3 символи)
    :param email: Електронна пошта
    :param password: Пароль (мінімум 6 символів)
    """
    username: str = Field(min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    """
    Схема логіну користувача.

    :param username: Ім’я користувача
    :param password: Пароль
    """
    username: str
    password: str


class Token(BaseModel):
    """
    Схема JWT токену.

    :param access_token: Токен доступу
    :param token_type: Тип токена (наприклад, 'bearer')
    """
    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    """
    Схема запиту для повторного надсилання електронного листа з підтвердженням.

    :param email: Електронна пошта користувача
    """
    email: EmailStr

class ResetPassword(BaseModel):
    password: str = Field(..., min_length=6)