"""
Модуль auth.py

Цей модуль містить функції та класи для аутентифікації користувачів, 
керування JWT-токенами, хешування паролів та отримання поточного користувача.

Функції:
---------
- create_email_token(data: dict): Генерує JWT-токен для підтвердження електронної пошти.
- get_email_from_token(token: str): Розшифровує токен і повертає email.
- create_access_token(data: dict, expires_delta: Optional[int] = None): Створює access токен.
- get_current_user(token: str, db: Session): Повертає поточного автентифікованого користувача.

Класи:
-------
- Hash: Обгортає функціональність для хешування і перевірки паролів.
"""

from datetime import datetime, timedelta, UTC, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt

from src.database.db import get_db
from src.conf.config import settings
from src.services.users import UserService
from src.services.cache import get_from_cache, set_to_cache
from src.database.models import User
from src.database.models import Role

UTC = timezone.utc


def create_email_token(data: dict):
    """
    Створює JWT-токен для підтвердження електронної пошти, що діє 7 днів.

    :param data: Дані, які будуть закодовані у токені.
    :return: JWT-токен як рядок.
    """
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


async def get_email_from_token(token: str):
    """
    Розшифровує email із токена підтвердження.

    :param token: JWT-токен, отриманий на email.
    :return: Електронна пошта (email), витягнута з токена.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        print(f"[DEBUG] Token payload: {payload}")
        return payload.get("sub")
    except JWTError as e:
        print(f"[ERROR] JWTError: {e}")
        raise HTTPException(
            status_code=422,
            detail="Неправильний токен для перевірки електронної пошти"
        )


class Hash:
    """
    Клас для хешування паролів та перевірки паролів.

    Методи:
    --------
    - get_password_hash: Хешує пароль.
    - verify_password: Перевіряє відповідність паролю та хешу.
    """
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        """
        Перевіряє, чи відповідає звичайний пароль хешованому.

        :param plain_password: Введений користувачем пароль.
        :param hashed_password: Збережений хеш пароля.
        :return: True або False.
        """
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str):
        """
        Повертає хеш пароля.

        :param password: Пароль користувача.
        :return: Хешований пароль.
        """
        return self.pwd_context.hash(password)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def create_access_token(data: dict, expires_delta: Optional[int] = None):
    """
    Створює access JWT-токен для автентифікації користувача.

    :param data: Дані, які потрібно закодувати.
    :param expires_delta: Час життя токена в секундах (опціонально).
    :return: JWT-токен як рядок.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=settings.JWT_EXPIRATION_SECONDS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Отримує поточного користувача з кешу або бази даних за токеном.

    :param token: JWT-токен.
    :param db: Сесія бази даних.
    :return: Об'єкт користувача (User).
    :raise HTTPException: Якщо токен невалідний або користувача не існує.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    cached_user = await get_from_cache(username)
    if cached_user:
        user = User(**cached_user)

        if isinstance(user.role, str):
            user.role = Role(user.role)

        return user

    user_service = UserService(db)
    user = await user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception

    await set_to_cache(username, {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "confirmed": user.confirmed,
        "avatar": user.avatar,
        "role": user.role.value,
    })
    return user

async def admin_required(current_user: User = Depends(get_current_user)):
    print(f"[DEBUG] current_user.role = {current_user.role}")
    if current_user.role != Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Тільки адміністратор може виконати цю дію"
        )
    return current_user