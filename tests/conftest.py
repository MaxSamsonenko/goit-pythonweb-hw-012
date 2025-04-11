import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.pool import StaticPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from main import app
from src.database.models import Base, User
from src.database.db import get_db
from src.services.auth import create_access_token, Hash
from sqlalchemy import select
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient, ASGITransport
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./test.db"
from unittest.mock import AsyncMock, patch

@pytest.fixture(autouse=True)
def mock_redis_cache():
    with patch("src.services.cache.get_from_cache", new_callable=AsyncMock) as mock_get, \
         patch("src.services.cache.set_to_cache", new_callable=AsyncMock) as mock_set:
        mock_get.return_value = None
        yield (mock_get, mock_set)

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)

@pytest.fixture(autouse=True)
def mock_redis_client(monkeypatch):
    class MockRedis:
        async def get(self, *args, **kwargs):
            return None

        async def set(self, *args, **kwargs):
            return None

    monkeypatch.setattr("src.services.cache.redis_client", MockRedis())

test_user = {
    "username": "deadpool",
    "email": "deadpool@example.com",
    "password": "12345678",
}

@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hashed_password = Hash().get_password_hash(test_user["password"])
            user = User(
                username=test_user["username"],
                email=test_user["email"],
                hashed_password=hashed_password,
                confirmed=True,
                role="admin",
                avatar="https://example.com/avatar.png",
            )
            session.add(user)
            await session.commit()

    asyncio.run(init_models())
    


@pytest_asyncio.fixture
async def async_client():
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app, raise_app_exceptions=True)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture
async def get_token():
    async with TestingSessionLocal() as session:
        user = await session.execute(select(User).where(User.email == test_user["email"]))
        user = user.scalar_one_or_none()
        return await create_access_token(data={"sub": user.username})

