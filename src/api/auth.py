"""
Модуль auth.py

Цей модуль відповідає за маршрути автентифікації та реєстрації користувача, включаючи:
- Реєстрацію нового користувача з підтвердженням електронної пошти
- Підтвердження email
- Вхід користувача
- Повторне надсилання листа підтвердження

Маршрути:
- POST /register
- GET /confirmed_email/{token}
- POST /login
- POST /request_email
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request, Form
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas import UserCreate, Token, User, RequestEmail
from src.services.auth import create_access_token, Hash, get_email_from_token
from src.services.users import UserService
from src.services.email import send_email, create_email_token
from src.database.db import get_db
from src.conf.config import settings
from jose import JWTError, jwt
from src.services.email import send_reset_password_email

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Реєстрація нового користувача.

    Перевіряє унікальність email та username,
    створює токен підтвердження, надсилає лист з посиланням.

    :param user_data: Дані нового користувача
    :param background_tasks: Менеджер фонових задач
    :param request: Об’єкт запиту FastAPI
    :param db: Сесія бази даних
    :return: Повідомлення про необхідність підтвердження пошти
    """
    user_service = UserService(db)

    email_user = await user_service.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким email вже існує",
        )

    username_user = await user_service.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Користувач з таким іменем вже існує",
        )
    token_data = {
        "email": user_data.email,
        "sub": user_data.email,
        "username": user_data.username,
        "password": Hash().get_password_hash(user_data.password)
    }
    token = create_email_token(token_data)

    background_tasks.add_task(
        send_email,
        user_data.email,
        user_data.username,
        str(request.base_url),
        token
    )
    return {"message": "Перевірте вашу пошту для підтвердження реєстрації"}


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    """
    Підтвердження електронної пошти користувача за токеном.

    Якщо токен дійсний і користувач не існує,
    створюється новий підтверджений користувач.

    :param token: JWT токен для підтвердження
    :param db: Сесія бази даних
    :return: Повідомлення про створення або наявність користувача
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        email = payload.get("sub")
        username = payload.get("username")
        password = payload.get("password")

        user_service = UserService(db)
        existing_user = await user_service.get_user_by_email(email)
        if existing_user:
            return {"message": "Користувач уже існує"}

        new_user = await user_service.create_user_from_data(email, username, password)
        return {
            "message": "Електронна пошта підтверджена, користувача створено"
        }
    except JWTError:
        raise HTTPException(status_code=422, detail="Невірний токен")


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    """
    Вхід користувача.

    Перевірка логіну і паролю, генерація токена доступу.

    :param form_data: Форма з логіном і паролем
    :param db: Сесія бази даних
    :return: Токен доступу
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user:
     raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неправильний логін або пароль",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильний логін або пароль",
            headers={"WWW-Authenticate": "Bearer"},
    )

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Електронна адреса не підтверджена",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = await create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Повторне надсилання листа з підтвердженням електронної пошти.

    :param body: Модель з email користувача
    :param background_tasks: Менеджер фонових задач
    :param request: Об’єкт запиту FastAPI
    :param db: Сесія бази даних
    :return: Повідомлення про надсилання листа
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)
    if user and not user.confirmed:
        background_tasks.add_task(
            send_email, user.email, user.username, str(request.base_url)
        )
    return {"message": "Перевірте свою електронну пошту для підтвердження"}

@router.post("/forgot-password", response_model=dict)
async def forgot_password(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Запит на скидання пароля (надсилання листа з токеном).

    :param body: email користувача
    :param background_tasks: менеджер фонових задач
    :param request: базовий URL хосту
    :param db: сесія БД
    :return: повідомлення
    """
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)

    if user:
        token_data = {"sub": user.email}
        token = create_email_token(token_data)
        background_tasks.add_task(
            send_reset_password_email, user.email, user.username, str(request.base_url), token
        )

    return {"message": "Якщо цей email існує — перевірте пошту для скидання пароля"}


@router.post("/reset-password/{token}", response_model=dict)
async def reset_password(token: str, new_password: str = Form(...), db: Session = Depends(get_db)):
    """
    Обробляє скидання пароля з HTML-форми.
    """
    try:
        email = await get_email_from_token(token)
    except HTTPException:
        raise HTTPException(status_code=400, detail="Невірний або прострочений токен")

    user_service = UserService(db)
    user = await user_service.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="Користувача не знайдено")

    user.hashed_password = Hash().get_password_hash(new_password)
    await db.commit()
    return {"message": "Пароль успішно змінено"}
    
templates = Jinja2Templates(directory="src/services/templates")

@router.get("/reset-password/{token}", response_class=HTMLResponse)
async def reset_password_form(token: str, request: Request):
    """
    Відображає HTML-форму для скидання пароля.
    """
    return templates.TemplateResponse("reset_password_form.html", {
        "request": request,
        "token": token
    })
    
    
@router.patch("/users/{user_id}/role", response_model=User)
async def change_user_role(user_id: int, new_role: str, db: Session = Depends(get_db)):
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if new_role not in ["admin", "user"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    user.role = new_role
    await db.commit()
    await db.refresh(user)
    return user