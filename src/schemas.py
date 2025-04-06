from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class ContactBase(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: EmailStr
    phone: str = Field(max_length=20)
    birthday: Optional[date] = None
    extra_info: Optional[str] = Field(default=None, max_length=250)


# Схема для створення контакту
class ContactCreate(ContactBase):
    pass


# Схема для оновлення контакту
class ContactUpdate(ContactBase):
    pass


# Схема відповіді (з бази)
class ContactResponse(ContactBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
    
# -------------------- USERS --------------------

# Схема для відповіді користувача з бази
class User(BaseModel):
    id: int
    username: str
    email: str
    avatar: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Схема для створення користувача
class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6)


# Схема для логіну (авторизації)
class UserLogin(BaseModel):
    username: str
    password: str


# Схема токену
class Token(BaseModel):
    access_token: str
    token_type: str


class RequestEmail(BaseModel):
    email: EmailStr