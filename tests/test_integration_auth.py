import pytest
from unittest.mock import Mock
from src.database.models import User
from src.services.auth import Hash
from tests.conftest import TestingSessionLocal

user_data = {
    "username": "agent007",
    "email": "agent007@gmail.com",
    "password": "12345678",
}


@pytest.mark.asyncio
async def test_signup(async_client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)

    response = await async_client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Перевірте вашу пошту для підтвердження реєстрації"


@pytest.mark.asyncio
async def test_repeat_signup(async_client, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.api.auth.send_email", mock_send_email)

    response = await async_client.post("/api/auth/register", json=user_data)
    assert response.status_code == 201
    assert response.json()["message"] == "Перевірте вашу пошту для підтвердження реєстрації"


@pytest.mark.asyncio
async def test_not_confirmed_login(async_client):
    async with TestingSessionLocal() as session:
        hashed_password = Hash().get_password_hash(user_data["password"])
        user = User(
            username="notconfirmed",
            email="notconfirmed@example.com",
            hashed_password=hashed_password,
            confirmed=False
        )
        session.add(user)
        await session.commit()

    response = await async_client.post("/api/auth/login", data={
        "username": "notconfirmed",
        "password": user_data["password"]
    })
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Електронна адреса не підтверджена"


@pytest.mark.asyncio
async def test_login(async_client):
    response = await async_client.post("/api/auth/login", data={
        "username": "deadpool",
        "password": "12345678"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


@pytest.mark.asyncio
async def test_wrong_password_login(async_client):
    response = await async_client.post("/api/auth/login", data={
        "username": user_data["username"],
        "password": "wrong_password"
    })
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Неправильний логін або пароль"


@pytest.mark.asyncio
async def test_wrong_username_login(async_client):
    response = await async_client.post("/api/auth/login", data={
        "username": "nonexistent_user",
        "password": user_data["password"]
    })
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Неправильний логін або пароль"


@pytest.mark.asyncio
async def test_validation_error_login(async_client):
    response = await async_client.post("/api/auth/login", data={
        "password": user_data["password"]
    })
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
