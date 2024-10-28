import pytest
from fastapi.testclient import TestClient
from app.main import app 
from app.test_db import init_db, drop_db, TestingSessionLocal
from app.repository import get_password_hash
from app import models


@pytest.fixture(scope="function")
def test_client():
    init_db()
    db = TestingSessionLocal()
    permission_admin = models.Permission(name="admin")
    permission_guest = models.Permission(name="guest")
    db.add(permission_admin)  
    db.add(permission_guest)
    db.commit()
    db.refresh(permission_admin)
    db.refresh(permission_guest)
    admin_user = models.User(
        email="admin@example.com",
        username="admin",
        name="John",
        surname="Doe",
        password=get_password_hash("G*qE/6r$"),  
    )
    db.add(admin_user)
    admin_user_2 = models.User(
        email="jack@example.com",
        username="JackDoe",
        name="Jack",
        surname="Doe",
        password=get_password_hash("G*qE/6r$"),  
    )
    db.add(admin_user_2)
    guest_user_1 = models.User(
        email="harry@example.com",
        username="HarryDoe",
        name="Harry",
        surname="Doe",
        password=get_password_hash("G*qE/6r$"),  
    )
    db.add(guest_user_1)
    db.commit()
    db.refresh(admin_user)
    db.refresh(admin_user_2)
    db.refresh(guest_user_1)
    db.add(models.UserPermission(user_id=admin_user.id, permission_id=permission_admin.id))
    db.add(models.UserPermission(user_id=admin_user_2.id, permission_id=permission_admin.id))
    db.add(models.UserPermission(user_id=guest_user_1.id, permission_id=permission_guest.id))
    db.commit()
    db.close()
    yield TestClient(app)
    drop_db()

def authenticate_admin(test_client):
    login_response = test_client.post(
        "/token",
        data={"username": "admin", "password": "G*qE/6r$"}  
    )
    return login_response.json()["access_token"]

def test_create_user(test_client):
    access_token = authenticate_admin(test_client)
    response = test_client.post(
        "/create_user",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"email": "testuser@example.com", "password": "G*qE/6r$", "username": "testuser", "name": "test", "surname": "user", "permissions": [1]}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert "id" in data

def test_not_authenticated_create_user(test_client):
    response = test_client.post(
        "/create_user",
        headers={"Authorization": "Bearer 1234"},
        json={"email": "testuser@example.com", "password": "G*qE/6r$", "username": "testuser", "name": "test", "surname": "user", "permissions": [1]}
    )
    assert response.status_code == 401

def test_not_authorized_create_user(test_client):
    login_response = test_client.post(
        "/token",
        data={"username": "HarryDoe", "password": "G*qE/6r$"}  
    )
    access_token =  login_response.json()["access_token"]
    assert login_response.status_code == 200
    response = test_client.post(
        "/create_user",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"email": "testuser@example.com", "password": "G*qE/6r$", "username": "testuser", "name": "test", "surname": "user", "permissions": [1]}
    )
    assert response.status_code == 403


def test_list_users_filter_by_all_params(test_client):
    access_token = authenticate_admin(test_client)
    response = test_client.get(
        "/list_users/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 3

def test_list_users_filter_by_email(test_client):
    access_token = authenticate_admin(test_client)
    response = test_client.get(
        "/list_users/",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"email": "harry@example.com"}
    )
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 1
    assert result[0]["email"] == "harry@example.com"

def test_list_users_filter_by_surname(test_client):
    access_token = authenticate_admin(test_client)
    response = test_client.get(
        "/list_users/",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"surname": "Doe"}
    )
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 3
    assert result[0]["surname"] == "Doe"
    assert result[1]["surname"] == "Doe"
    assert result[2]["surname"] == "Doe"

def test_list_users_filter_by_name(test_client):
    access_token = authenticate_admin(test_client)
    response = test_client.get(
        "/list_users/",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"name": "Harry"}
    )
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 1
    assert result[0]["name"] == "Harry"