import pytest
from fastapi.testclient import TestClient
from app.main import app  
from app.test_db import init_db, drop_db, TestingSessionLocal
from app.repository import get_password_hash
from app import models

@pytest.fixture(scope="module")
def test_client():
    init_db()
    db = TestingSessionLocal()  
    admin_user = models.User(
        email="admin@example.com",
        username="admin",
        name="John",
        surname="Doe",
        password=get_password_hash("admin_password"),  
        user_level="admin"
    )
    db.add(admin_user)
    db.commit()
    db.close()
    yield TestClient(app)
    drop_db()

def test_example(test_client):
    response = test_client.get("/users/2")
    assert response.status_code == 404

def test_create_user(test_client):
    login_response = test_client.post(
        "/token",
        data={"username": "admin", "password": "admin_password"}  
    )
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]
    response = test_client.post(
        "/create_user",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"email": "testuser@example.com", "password": "password", "username": "testuser", "name": "test", "surname": "user", "user_level": "guest"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@example.com"
    assert "id" in data