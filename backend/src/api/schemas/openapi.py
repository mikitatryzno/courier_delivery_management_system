"""OpenAPI schema definitions and examples."""
from typing import Dict, Any

# Example data for API documentation
EXAMPLE_USER_CREATE = {
    "email": "john.doe@example.com",
    "name": "John Doe",
    "password": "securepassword123",
    "role": "sender",
    "phone": "+1234567890"
}

EXAMPLE_USER_LOGIN = {
    "email": "john.doe@example.com",
    "password": "securepassword123"
}

EXAMPLE_USER_RESPONSE = {
    "id": 1,
    "email": "john.doe@example.com",
    "name": "John Doe",
    "role": "sender",
    "phone": "+1234567890",
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z"
}

EXAMPLE_TOKEN_RESPONSE = {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "expires_in": 1800,
    "user": EXAMPLE_USER_RESPONSE
}

EXAMPLE_PACKAGE_CREATE = {
    "title": "Important Documents",
    "description": "Legal documents that need urgent delivery",
    "sender_name": "John Doe",
    "sender_phone": "+1234567890",
    "sender_address": "123 Main St, City, State 12345",
    "recipient_name": "Jane Smith",
    "recipient_phone": "+1234567891",
    "recipient_address": "456 Oak Ave, City, State 12346"
}

EXAMPLE_PACKAGE_RESPONSE = {
    "id": 1,
    "title": "Important Documents",
    "description": "Legal documents that need urgent delivery",
    "status": "created",
    "sender_name": "John Doe",
    "sender_phone": "+1234567890",
    "sender_address": "123 Main St, City, State 12345",
    "recipient_name": "Jane Smith",
    "recipient_phone": "+1234567891",
    "recipient_address": "456 Oak Ave, City, State 12346",
    "sender_id": 1,
    "courier_id": None,
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T10:00:00Z"
}

EXAMPLE_PACKAGE_STATUS_UPDATE = {
    "status": "assigned"
}

EXAMPLE_WEBSOCKET_MESSAGE = {
    "type": "package_update",
    "package_id": 1,
    "package": EXAMPLE_PACKAGE_RESPONSE,
    "message": "Package status updated to assigned",
    "timestamp": "2024-01-01T10:30:00Z"
}

EXAMPLE_ERROR_RESPONSE = {
    "detail": "Error description"
}

EXAMPLE_VALIDATION_ERROR = {
    "detail": [
        {
            "loc": ["body", "email"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ]
}

# OpenAPI response examples
OPENAPI_RESPONSES: Dict[str, Dict[str, Any]] = {
    "401": {
        "description": "Authentication required",
        "content": {
            "application/json": {
                "example": {"detail": "Not authenticated"}
            }
        }
    },
    "403": {
        "description": "Insufficient permissions",
        "content": {
            "application/json": {
                "example": {"detail": "Access denied. Required role: admin"}
            }
        }
    },
    "404": {
        "description": "Resource not found",
        "content": {
            "application/json": {
                "example": {"detail": "Resource not found"}
            }
        }
    },
    "422": {
        "description": "Validation error",
        "content": {
            "application/json": {
                "example": EXAMPLE_VALIDATION_ERROR
            }
        }
    },
    "500": {
        "description": "Internal server error",
        "content": {
            "application/json": {
                "example": {"detail": "Internal server error"}
            }
        }
    }
}

# Common OpenAPI parameters
OPENAPI_PARAMETERS = {
    "package_id": {
        "name": "package_id",
        "in": "path",
        "required": True,
        "schema": {"type": "integer", "minimum": 1},
        "description": "Unique identifier for the package",
        "example": 1
    },
    "user_id": {
        "name": "user_id",
        "in": "path",
        "required": True,
        "schema": {"type": "integer", "minimum": 1},
        "description": "Unique identifier for the user",
        "example": 1
    },
    "skip": {
        "name": "skip",
        "in": "query",
        "required": False,
        "schema": {"type": "integer", "minimum": 0, "default": 0},
        "description": "Number of records to skip for pagination",
        "example": 0
    },
    "limit": {
        "name": "limit",
        "in": "query",
        "required": False,
        "schema": {"type": "integer", "minimum": 1, "maximum": 100, "default": 10},
        "description": "Maximum number of records to return",
        "example": 10
    }
}