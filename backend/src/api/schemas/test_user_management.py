"""Tests for user management functionality."""
import pytest
from fastapi.testclient import TestClient
from src.models.user import User, UserRole
from src.core.security import get_password_hash

def test_list_users_admin(client, admin_headers, db_session):
    """Test listing users as admin."""
    response = client.get("/api/users/", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_list_users_non_admin(client, auth_headers):
    """Test listing users as non-admin (should fail)."""
    response = client.get("/api/users/", headers=auth_headers)
    assert response.status_code == 403

def test_get_my_profile(client, auth_headers):
    """Test getting own profile."""
    response = client.get("/api/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "email" in data
    assert "name" in data

def test_update_my_profile(client, auth_headers):
    """Test updating own profile."""
    update_data = {
        "name": "Updated Name",
        "phone": "+1234567890"
    }
    response = client.put("/api/users/me", headers=auth_headers, json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["phone"] == "+1234567890"

def test_get_user_by_id_admin(client, admin_headers, test_user):
    """Test getting user by ID as admin."""
    response = client.get(f"/api/users/{test_user.id}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_user.id

def test_get_user_by_id_own_profile(client, auth_headers, test_user):
    """Test getting own profile by ID."""
    response = client.get(f"/api/users/{test_user.id}", headers=auth_headers)
    assert response.status_code == 200

def test_get_user_by_id_unauthorized(client, auth_headers):
    """Test getting other user's profile (should fail)."""
    response = client.get("/api/users/999", headers=auth_headers)
    assert response.status_code == 403

def test_update_user_role_admin(client, admin_headers, db_session):
    """Test updating user role as admin."""
    # Create test user
    user = User(
        email="roletest@example.com",
        name="Role Test User",
        hashed_password=get_password_hash("testpass"),
        role=UserRole.SENDER
    )
    db_session.add(user)
    db_session.commit()
    
    # Update role
    response = client.put(
        f"/api/users/{user.id}/role",
        headers=admin_headers,
        json={"role": "courier"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "courier"

def test_delete_user_admin(client, admin_headers, db_session):
    """Test deleting user as admin."""
    # Create test user
    user = User(
        email="deletetest@example.com",
        name="Delete Test User",
        hashed_password=get_password_hash("testpass"),
        role=UserRole.SENDER
    )
    db_session.add(user)
    db_session.commit()
    
    # Delete user
    response = client.delete(f"/api/users/{user.id}", headers=admin_headers)
    assert response.status_code == 200

def test_get_users_by_role(client, admin_headers):
    """Test getting users by role."""
    response = client.get("/api/users/role/sender", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_user_stats_admin(client, admin_headers):
    """Test getting user statistics as admin."""
    response = client.get("/api/users/stats/summary", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "users_by_role" in data
    assert "recent_registrations" in data

def test_search_users(client, admin_headers):
    """Test searching users."""
    response = client.get("/api/users/?search=test", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_pagination(client, admin_headers):
    """Test user list pagination."""
    response = client.get("/api/users/?skip=0&limit=5", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 5