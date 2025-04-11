"""
Модуль cloudinary.py

Цей модуль конфігурує підключення до сервісу Cloudinary для роботи з мультимедійними файлами.

Використовується для завантаження, оновлення, видалення зображень та інших ресурсів у хмарне сховище Cloudinary.

Налаштування беруться з конфігураційного файлу (через `settings` з src.conf.config).

Приклад:
--------
    import cloudinary.uploader
    result = cloudinary.uploader.upload(file_path)

Змінні середовища, які мають бути задані:
------------------------------------------
- CLOUDINARY_NAME
- CLOUDINARY_API_KEY
- CLOUDINARY_API_SECRET
"""

import cloudinary

from src.conf.config import settings

cloudinary.config(
    cloud_name=settings.CLOUDINARY_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)
