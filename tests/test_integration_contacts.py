import pytest
from datetime import date, timedelta

@pytest.mark.asyncio
async def test_create_contact(async_client, get_token):
    contact_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890",
        "birthday": "1990-01-01",
        "extra_data": "Friend from college"
    }
    response = await async_client.post(
        "/api/contacts/",
        json=contact_data,
        headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == contact_data["email"]
    test_create_contact.contact_id = data["id"]  


@pytest.mark.asyncio
async def test_read_contacts(async_client, get_token):
    response = await async_client.get(
        "/api/contacts/",
        headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_read_single_contact(async_client, get_token):
    response = await async_client.get(
        f"/api/contacts/{test_create_contact.contact_id}",
        headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_create_contact.contact_id


@pytest.mark.asyncio
async def test_update_contact(async_client, get_token):
    updated_data = {
        "first_name": "Johnny",
        "last_name": "Doe",
        "email": "johnny.doe@example.com",
        "phone": "+1987654321",
        "birthday": "1991-02-02",
        "extra_data": "Updated info"
    }
    response = await async_client.put(
        f"/api/contacts/{test_create_contact.contact_id}",
        json=updated_data,
        headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == updated_data["email"]


@pytest.mark.asyncio
async def test_search_contacts(async_client, get_token):
    response = await async_client.get(
        "/api/contacts/search/?query=Johnny",
        headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200
    results = response.json()
    assert any("Johnny" in contact["first_name"] for contact in results)


@pytest.mark.asyncio
async def test_upcoming_birthdays(async_client, get_token):
    today = date.today()
    near_birthday = (today + timedelta(days=3)).strftime("%Y-%m-%d")

    await async_client.post(
        "/api/contacts/",
        json={
            "first_name": "Birthday",
            "last_name": "Soon",
            "email": "bday@example.com",
            "phone": "+1230000000",
            "birthday": near_birthday,
            "extra_data": "Test birthday"
        },
        headers={"Authorization": f"Bearer {get_token}"}
    )

    response = await async_client.get(
        "/api/contacts/birthdays/?days=5",
        headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200
    results = response.json()
    assert any("Birthday" in contact["first_name"] for contact in results)


@pytest.mark.asyncio
async def test_delete_contact(async_client, get_token):
    response = await async_client.delete(
        f"/api/contacts/{test_create_contact.contact_id}",
        headers={"Authorization": f"Bearer {get_token}"}
    )
    assert response.status_code == 200
    deleted = response.json()
    assert deleted["id"] == test_create_contact.contact_id
