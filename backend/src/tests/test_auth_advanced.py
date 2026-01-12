"""Advanced authentication tests."""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from src.core.security import create_access_token, create_refresh_token, is_token_expired
from src.utils.jwt_utils import jwt_manager
from src.models.user import UserRole

def test_token_expiry(client, test_user):
    """Test token expiry functionality."""
    # Create expired token
    expired_token = create_access_token(
        data={"sub": str(test_user.id)},
        expires_delta=timedelta(seconds=-1)  # Already expired
    )
    
    # Test with expired token
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    assert response.status_code == 401

def test_refresh_token_flow(client, test_user):
    """Test refresh token functionality."""
    # Login to get tokens
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "testpass"
    })
    assert response.status_code == 200
    
    # Create refresh token manually for testing
    refresh_token = create_refresh_token({"sub": str(test_user.id)})
    
    # Use refresh token to get new access token
    response = client.post("/api/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_invalid_token_type(client, test_user):
    """Test using refresh token as access token."""
    refresh_token = create_refresh_token({"sub": str(test_user.id)})
    
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {refresh_token}"}
    )
    assert response.status_code == 401

def test_token_info_endpoint(client, auth_headers):
    """Test token information endpoint."""
    response = client.get("/api/auth/token-info", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data
    assert "email" in data
    assert "role" in data
    assert "expires_at" in data

def test_change_password(client, auth_headers, test_user, db_session):
    """Test password change functionality."""
    response = client.post("/api/auth/change-password", 
        headers=auth_headers,
        json={
            "current_password": "testpass",
            "new_password": "newtestpass"
        }
    )
    assert response.status_code == 200
    
    # Test login with new password
    response = client.post("/api/auth/login", json={
        "email": "test@example.com",
        "password": "newtestpass"
    })
    assert response.status_code == 200

def test_role_based_access(client, db_session):
    """Test role-based access control."""
    from src.models.user import User
    from src.core.security import get_password_hash
    
    # Create courier user
    courier = User(
        email="courier@test.com",
        name="Test Courier",
        hashed_password=get_password_hash("testpass"),
        role=UserRole.COURIER
    )
    db_session.add(courier)
    db_session.commit()
    
    # Login as courier
    response = client.post("/api/auth/login", json={
        "email": "courier@test.com",
        "password": "testpass"
    })
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Try to access admin endpoint (should fail)
    response = client.get(
        "/api/users/",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403

def test_jwt_utils(test_user):
    """Test JWT utility functions."""
    # Test token creation
    token = jwt_manager.create_access_token({"sub": str(test_user.id)})
    assert token is not None
    
    # Test token verification
    payload = jwt_manager.verify_token(token)
    assert payload["sub"] == str(test_user.id)
    
    # Test token expiry check
    assert not jwt_manager.is_token_expired(token)
    
    # Test expired token
    expired_token = jwt_manager.create_access_token(
        {"sub": str(test_user.id)},
        timedelta(seconds=-1)
    )
    assert jwt_manager.is_token_expired(expired_token)

def test_malformed_token(client):
    """Test handling of malformed tokens."""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 401

def test_missing_authorization_header(client):
    """Test missing authorization header."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401

def test_validate_token_endpoint(client, auth_headers):
    """Test token validation endpoint."""
    response = client.get("/api/auth/validate", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert "user_id" in data
    assert "email" in data
    assert "role" in data