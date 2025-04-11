"""
Модуль config.py

Цей модуль містить конфігураційний клас Settings, який використовує бібліотеку `pydantic_settings`
для зчитування налаштувань із файлу `.env`. Клас забезпечує централізоване управління конфігурацією,
включаючи налаштування бази даних, JWT-токенів, електронної пошти та Cloudinary.
"""

from pydantic import EmailStr
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv() 


class Settings(BaseSettings):
    """
    Клас конфігурації для FastAPI-застосунку.

    Зчитує значення змінних середовища з `.env` файлу для:
    - Підключення до бази даних (ASYNC і SYNC)
    - Налаштування JWT токенів
    - Параметри електронної пошти (SMTP)
    - Параметри Cloudinary для зберігання зображень
    """

    DB_URL: str
    SYNC_DB_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600

    MAIL_USERNAME: EmailStr
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str = "FastAPI App"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    CLOUDINARY_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    class Config:
        """
        Конфігурація для класу Settings.
        """
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  
        

settings = Settings()
