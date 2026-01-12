import pytest
from fastapi.testclient import TestClient

def test_login_success(client, test_user):
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "testpass"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"

def test_login_invalid_credentials(client):
    response = client.post("/api/auth/login", json={
        "email": "wrong@example.com",
        "password": "wrongpass"
    })
    assert response.status_code == 401

def test_register_success(client):
    response = client.post("/api/auth/register", json={
        "email": "new@example.com",
        "name": "New User",
        "password": "newpass",
        "role": "sender"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["name"] == "New User"

def test_get_current_user(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"