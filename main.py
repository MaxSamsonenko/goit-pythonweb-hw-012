"""
Модуль main

Це основний модуль запуску FastAPI-застосунку для менеджера контактів.

- Ініціалізує FastAPI застосунок з відповідними middleware.
- Додає підтримку CORS для клієнта на `http://localhost:3000`.
- Реєструє маршрути з модулів `contacts`, `auth`, `users`.
- Використовує обмеження швидкості запитів через `slowapi`.
- Визначає обробку винятку при перевищенні ліміту запитів (429 Too Many Requests).
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from src.api import contacts, auth, users
import asyncio
import sys

if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

origins = [
    "http://localhost:3000",
]

# Ініціалізація FastAPI-застосунку
app = FastAPI(title="Contact Manager API")

# Додавання CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Дозволені домени
    allow_credentials=True,          # Дозвіл на передачу куків
    allow_methods=["*"],             # Дозволені HTTP методи
    allow_headers=["*"],             # Дозволені заголовки
)

# Налаштування обмеження запитів (Rate limiting)
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Обробка винятку, коли користувач перевищує дозволену кількість запитів.

    :param request: Поточний HTTP-запит
    :param exc: Виняток типу RateLimitExceeded
    :return: JSON відповідь з кодом 429
    """
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": "Перевищено ліміт запитів. Спробуйте пізніше."},
    )

app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")

# Запуск застосунку через uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
