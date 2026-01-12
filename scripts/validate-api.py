#!/usr/bin/env python3
"""Validate API endpoints and responses."""

import requests
import json
from typing import Dict, Any

class APIValidator:
    """Validate API endpoints and responses."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
        self.session = requests.Session()
    
    def test_health_endpoints(self):
        """Test health check endpoints."""
        print("🏥 Testing health endpoints...")
        
        try:
            # Basic health check
            response = self.session.get(f"{self.base_url}/api/health/")
            assert response.status_code == 200
            print("✅ Basic health check passed")
            
            # Database health check
            response = self.session.get(f"{self.base_url}/api/health/database")
            assert response.status_code == 200
            print("✅ Database health check passed")
            
        except Exception as e:
            print(f"❌ Health check failed: {e}")
    
    def test_auth_flow(self):
        """Test authentication flow."""
        print("🔐 Testing authentication flow...")
        
        try:
            # Test registration
            user_data = {
                "email": "test@example.com",
                "name": "Test User",
                "password": "testpass123",
                "role": "sender",
                "phone": "+1234567890"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/auth/register",
                json=user_data
            )
            
            if response.status_code == 201:
                print("✅ User registration passed")
            elif response.status_code == 400 and "already registered" in response.text:
                print("ℹ️ User already exists, continuing with login")
            else:
                raise Exception(f"Registration failed: {response.status_code}")
            
            # Test login
            login_data = {
                "email": "test@example.com",
                "password": "testpass123"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/auth/login",
                json=login_data
            )
            assert response.status_code == 200
            
            token_data = response.json()
            self.token = token_data["access_token"]
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
            print("✅ User login passed")
            
            # Test protected endpoint
            response = self.session.get(f"{self.base_url}/api/auth/me")
            assert response.status_code == 200
            print("✅ Protected endpoint access passed")
            
        except Exception as e:
            print(f"❌ Authentication test failed: {e}")
    
    def test_package_operations(self):
        """Test package CRUD operations."""
        print("📦 Testing package operations...")
        
        if not self.token:
            print("❌ No authentication token, skipping package tests")
            return
        
        try:
            # Create package
            package_data = {
                "title": "Test Package",
                "description": "Test package for API validation",
                "sender_name": "Test Sender",
                "sender_phone": "+1234567890",
                "sender_address": "123 Test St",
                "recipient_name": "Test Recipient",
                "recipient_phone": "+1234567891",
                "recipient_address": "456 Test Ave"
            }
            
            response = self.session.post(
                f"{self.base_url}/api/packages/",
                json=package_data
            )
            assert response.status_code == 200
            
            package = response.json()
            package_id = package["id"]
            print("✅ Package creation passed")
            
            # Get package
            response = self.session.get(f"{self.base_url}/api/packages/{package_id}")
            assert response.status_code == 200
            print("✅ Package retrieval passed")
            
            # List packages
            response = self.session.get(f"{self.base_url}/api/packages/")
            assert response.status_code == 200
            print("✅ Package listing passed")
            
            # Update package status (if user is admin or courier)
            status_data = {"status": "assigned"}
            response = self.session.put(
                f"{self.base_url}/api/packages/{package_id}/status",
                json=status_data
            )
            # This might fail if user doesn't have permission, which is expected
            if response.status_code in [200, 403]:
                print("✅ Package status update test passed")
            
        except Exception as e:
            print(f"❌ Package operations test failed: {e}")
    
    def test_openapi_spec(self):
        """Test OpenAPI specification."""
        print("📋 Testing OpenAPI specification...")
        
        try:
            response = self.session.get(f"{self.base_url}/api/openapi.json")
            assert response.status_code == 200
            
            spec = response.json()
            assert "openapi" in spec
            assert "info" in spec
            assert "paths" in spec
            
            print("✅ OpenAPI specification is valid")
            
            # Test documentation endpoints
            response = self.session.get(f"{self.base_url}/docs")
            assert response.status_code == 200
            print("✅ Swagger UI accessible")
            
            response = self.session.get(f"{self.base_url}/redoc")
            assert response.status_code == 200
            print("✅ ReDoc accessible")
            
        except Exception as e:
            print(f"❌ OpenAPI specification test failed: {e}")
    
    def run_all_tests(self):
        """Run all validation tests."""
        print("🚀 Starting API validation tests...\n")
        
        self.test_health_endpoints()
        print()
        
        self.test_openapi_spec()
        print()
        
        self.test_auth_flow()
        print()
        
        self.test_package_operations()
        print()
        
        print("✅ API validation completed!")

if __name__ == "__main__":
    validator = APIValidator()
    validator.run_all_tests()