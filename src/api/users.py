from fastapi import APIRouter, UploadFile, File, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import get_db
from src.services.auth import get_current_user
from src.database.models import User
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter

from src.schemas import User
from src.services.auth import get_current_user

import cloudinary
import cloudinary.uploader

from src.conf.config import settings

router = APIRouter(prefix="/users", tags=["users"])

limiter = Limiter(key_func=get_remote_address)

@router.get("/me", response_model=User, description="Максимум 5 запитів на хвилину")
@limiter.limit("5/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    return user

@router.post("/avatar")
async def update_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )

    upload_result = cloudinary.uploader.upload(file.file, folder="avatars", public_id=str(current_user.id))
    avatar_url = upload_result.get("secure_url")

    current_user.avatar = avatar_url
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)

    return {"avatar_url": avatar_url}