"""
Модуль users.py

Маршрути для взаємодії з обліковими записами користувачів:
- Отримання інформації про поточного користувача
- Оновлення аватара користувача через Cloudinary

Маршрути потребують авторизації через JWT.
"""

from fastapi import APIRouter, UploadFile, File, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.services.auth import admin_required, get_current_user
from src.database.models import User
from slowapi.util import get_remote_address
from slowapi import Limiter

import cloudinary
import cloudinary.uploader

from src.conf.config import settings
from src.schemas import User

router = APIRouter(prefix="/users", tags=["users"])

limiter = Limiter(key_func=get_remote_address)


@router.get("/me", response_model=User, description="Максимум 5 запитів на хвилину")
@limiter.limit("5/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    """
    Отримати профіль поточного авторизованого користувача.

    :param request: Запит HTTP
    :param user: Авторизований користувач
    :return: Дані користувача
    """
    return user


@router.post("/avatar")
async def update_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    print(f"[DEBUG] User role: {current_user.role}")
    """
    Оновити аватар користувача, завантаживши файл на Cloudinary.

    :param file: Файл зображення для нового аватара
    :param db: Сесія бази даних
    :param current_user: Авторизований користувач
    :return: Посилання на новий аватар
    """
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )

    upload_result = cloudinary.uploader.upload(
        file.file, folder="avatars", public_id=str(current_user.id)
    )
    avatar_url = upload_result.get("secure_url")

    current_user.avatar = avatar_url
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    return {"avatar_url": avatar_url}
