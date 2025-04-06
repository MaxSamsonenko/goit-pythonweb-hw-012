from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from src.schemas import UserCreate, Token, User, RequestEmail
from src.services.auth import create_access_token, Hash, get_email_from_token
from src.services.users import UserService
from src.services.email import send_email, create_email_token
from src.database.db import get_db
from src.conf.config import settings
from jose import JWTError, jwt

router = APIRouter(prefix="/auth", tags=["auth"])

# Реєстрація користувача
@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)):
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

# Логін користувача
@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user_service = UserService(db)
    user = await user_service.get_user_by_username(form_data.username)
    if not user or not Hash().verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неправильний логін або пароль",
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
    user_service = UserService(db)
    user = await user_service.get_user_by_email(body.email)
    if user and not user.confirmed:
        background_tasks.add_task(
            send_email, user.email, user.username, str(request.base_url)
        )
    return {"message": "Перевірте свою електронну пошту для підтвердження"}
