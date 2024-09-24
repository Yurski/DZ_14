import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    response = client.post("/register/", json={"email": "test@example.com", "password": "password"})
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
