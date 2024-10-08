import pytest
from fastapi.testclient import TestClient
from app.main import app  
from app.test_db import init_db, drop_db, TestingSessionLocal

@pytest.fixture(scope="module")
def test_client():
    init_db()
    yield TestClient(app)
    drop_db()

def test_example(test_client):
    response = test_client.get("/users/2")
    assert response.status_code == 404