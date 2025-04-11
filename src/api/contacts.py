"""
Модуль contacts.py

Маршрути для роботи з контактами користувача:
- Отримання списку контактів
- Отримання одного контакту
- Створення нового контакту
- Оновлення існуючого контакту
- Видалення контакту
- Пошук контактів за ключовим словом
- Отримання найближчих днів народжень

Усі маршрути захищені авторизацією.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.schemas import ContactCreate, ContactUpdate, ContactResponse
from src.services.contacts import ContactService
from src.database.models import User
from src.services.auth import get_current_user

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Отримати список контактів користувача з пагінацією.

    :param skip: Кількість пропущених записів
    :param limit: Максимальна кількість результатів
    :param db: Сесія бази даних
    :param user: Поточний авторизований користувач
    :return: Список контактів
    """
    service = ContactService(db)
    return await service.get_contacts(user.id, skip, limit)


@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Отримати контакт за ідентифікатором.

    :param contact_id: Ідентифікатор контакту
    :param db: Сесія бази даних
    :param user: Поточний авторизований користувач
    :return: Контакт або помилка 404
    """
    service = ContactService(db)
    contact = await service.get_contact(contact_id, user)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Створити новий контакт.

    :param body: Дані нового контакту
    :param db: Сесія бази даних
    :param user: Поточний авторизований користувач
    :return: Створений контакт
    """
    service = ContactService(db)
    return await service.create_contact(body, user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    body: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Оновити існуючий контакт.

    :param contact_id: Ідентифікатор контакту
    :param body: Нові дані контакту
    :param db: Сесія бази даних
    :param user: Поточний авторизований користувач
    :return: Оновлений контакт або помилка 404
    """
    service = ContactService(db)
    contact = await service.update_contact(contact_id, body, user)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Видалити контакт за ідентифікатором.

    :param contact_id: Ідентифікатор контакту
    :param db: Сесія бази даних
    :param user: Поточний авторизований користувач
    :return: Видалений контакт або помилка 404
    """
    service = ContactService(db)
    contact = await service.remove_contact(contact_id, user)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.get("/search/", response_model=List[ContactResponse])
async def search_contacts(
    query: str,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Пошук контактів за ім'ям, прізвищем або email.

    :param query: Пошуковий запит
    :param db: Сесія бази даних
    :param user: Поточний авторизований користувач
    :return: Список знайдених контактів
    """
    service = ContactService(db)
    return await service.search_contacts(query, user)


@router.get("/birthdays/", response_model=List[ContactResponse])
async def upcoming_birthdays(
    days: int = 7,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Отримати список контактів з днями народження протягом заданої кількості днів.

    :param days: Кількість днів наперед для перевірки
    :param db: Сесія бази даних
    :param user: Поточний авторизований користувач
    :return: Список контактів з днями народження
    """
    service = ContactService(db)
    return await service.get_upcoming_birthdays(days, user)
