import pytest
from tests.conftest import  test_user


@pytest.mark.asyncio
async def test_get_current_user(async_client, get_token, mock_redis_cache):
    response = await async_client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_user["email"]
    assert data["username"] == test_user["username"]
    assert "avatar" in data



@pytest.mark.asyncio
async def test_update_avatar(async_client, get_token, mock_redis_cache):
    with open("tests/assets/avatar.png", "rb") as f:
        response = await async_client.post(
            "/api/users/avatar",
            headers={"Authorization": f"Bearer {get_token}"},
            files={"file": ("avatar.png", f, "image/png")}
        )

    assert response.status_code == 200
    data = response.json()
    assert "avatar_url" in data
    assert data["avatar_url"].startswith("https://res.cloudinary.com")