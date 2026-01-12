"""OpenAPI configuration and customization."""
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI
from src.core.config import settings

def custom_openapi(app: FastAPI):
    """Generate custom OpenAPI schema."""
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=settings.project_name,
        version="1.0.0",
        description="""
        ## Courier Delivery Management System API

        A comprehensive API for managing courier delivery operations with real-time tracking and updates.

        ### Features
        - **User Management**: Authentication and role-based access control
        - **Package Management**: Create, track, and manage delivery packages
        - **Real-time Updates**: WebSocket connections for live notifications
        - **Role-based Access**: Admin, Courier, Sender, and Recipient roles
        - **Status Tracking**: Complete package lifecycle management

        ### Authentication
        This API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:
        ```
        Authorization: Bearer <your-jwt-token>
        ```

        ### User Roles
        - **Admin**: Full system access and management
        - **Courier**: Manage assigned packages and update delivery status
        - **Sender**: Create packages and track deliveries
        - **Recipient**: View packages addressed to them

        ### Getting Started
        1. Register a new user account
        2. Login to receive an access token
        3. Use the token to access protected endpoints
        4. Connect to WebSocket for real-time updates

        ### Support
        For support and documentation, visit our [GitHub repository](https://github.com/your-org/courier-delivery-system).
        """,
        routes=app.routes,
        contact={
            "name": "Courier Delivery System Support",
            "email": "support@courier-delivery.com",
            "url": "https://github.com/your-org/courier-delivery-system"
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT"
        },
        servers=[
            {
                "url": "http://localhost:8000",
                "description": "Development server"
            },
            {
                "url": "https://api.courier-delivery.com",
                "description": "Production server"
            }
        ]
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "JWT token obtained from /api/auth/login endpoint"
        }
    }
    
    # Add global security requirement
    openapi_schema["security"] = [{"BearerAuth": []}]
    
    # Add custom tags
    openapi_schema["tags"] = [
        {
            "name": "authentication",
            "description": "User authentication and authorization operations"
        },
        {
            "name": "users",
            "description": "User management operations"
        },
        {
            "name": "packages",
            "description": "Package management and tracking operations"
        },
        {
            "name": "websocket",
            "description": "Real-time WebSocket connections"
        },
        {
            "name": "health",
            "description": "System health and monitoring endpoints"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema