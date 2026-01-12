import pytest
from fastapi.testclient import TestClient

def test_create_package(client, auth_headers):
    package_data = {
        "title": "Test Package",
        "description": "Test Description",
        "sender_name": "Test Sender",
        "sender_phone": "+1234567890",
        "sender_address": "123 Test St",
        "recipient_name": "Test Recipient",
        "recipient_phone": "+1234567891",
        "recipient_address": "456 Test Ave"
    }
    
    response = client.post("/api/packages/", json=package_data, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Package"
    assert data["status"] == "created"

def test_get_packages(client, auth_headers):
    response = client.get("/api/packages/", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_package_unauthorized(client):
    response = client.get("/api/packages/")
    assert response.status_code == 401