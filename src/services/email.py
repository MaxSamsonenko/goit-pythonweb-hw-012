"""
Модуль services.email

Цей модуль відповідає за надсилання електронних листів користувачам.
Зокрема, реалізовано функцію надсилання листа з підтвердженням електронної пошти
після реєстрації користувача.

Використовується бібліотека `FastAPI-Mail` для асинхронного надсилання листів і шаблонів Jinja2.

Конфігурація поштового сервера береться з файлу `.env` через Pydantic `Settings`.

Функції:
--------
- send_email: Надсилає електронний лист із посиланням для підтвердження email.

Константи:
----------
- conf: Об'єкт конфігурації з параметрами для поштового клієнта FastMail.
"""

from pathlib import Path
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr
from src.services.auth import create_email_token
from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=settings.USE_CREDENTIALS,
    VALIDATE_CERTS=settings.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates"
)

async def send_email(email: EmailStr, username: str, host: str, token: str):
    """
    Надсилає лист підтвердження електронної адреси користувачу.

    :param email: Email користувача
    :type email: EmailStr
    :param username: Ім'я користувача
    :type username: str
    :param host: Базова адреса хосту застосунку (наприклад, http://127.0.0.1:8000)
    :type host: str
    :param token: JWT-токен для підтвердження
    :type token: str
    """
    try:
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token},
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)

async def send_reset_password_email(email: EmailStr, username: str, host: str, token: str):
    """
    Надсилає листа для скидання пароля.

    :param email: Email користувача
    :param username: Ім’я користувача
    :param host: Адреса хосту (http://127.0.0.1:8000/)
    :param token: JWT-токен
    """
    try:
        message = MessageSchema(
            subject="Access restoration",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token},
            subtype=MessageType.html
        )
        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset_password.html")
    except ConnectionErrors as err:
        print(f"Email send error: {err}")