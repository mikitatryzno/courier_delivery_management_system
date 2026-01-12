# API Documentation

## Overview

The Courier Delivery Management System API provides comprehensive endpoints for managing courier delivery operations with real-time tracking and updates.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.courier-delivery.com`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:


## Authorization: Bearer


### Getting a Token

1. **Register** a new account: `POST /api/auth/register`
2. **Login** with credentials: `POST /api/auth/login`
3. Use the returned `access_token` for subsequent requests

## API Documentation

### Interactive Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/api/openapi.json`

### Core Endpoints

#### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh access token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/logout` - User logout

#### Users
- `GET /api/users/` - List users (Admin only)
- `GET /api/users/{user_id}` - Get user by ID
- `PUT /api/users/{user_id}` - Update user
- `DELETE /api/users/{user_id}` - Delete user (Admin only)

#### Packages
- `GET /api/packages/` - List packages
- `POST /api/packages/` - Create package
- `GET /api/packages/{package_id}` - Get package details
- `PUT /api/packages/{package_id}` - Update package
- `PUT /api/packages/{package_id}/status` - Update package status
- `DELETE /api/packages/{package_id}` - Delete package

#### WebSocket
- `WS /api/ws/connect?token=<jwt_token>` - Real-time updates

#### Health
- `GET /api/health/` - Basic health check
- `GET /api/health/database` - Database health check

## User Roles

### Admin
- Full system access
- User management
- All package operations
- System monitoring

### Courier
- View assigned packages
- Update package status
- Real-time notifications

### Sender
- Create packages
- Track own packages
- Receive delivery updates

### Recipient
- View packages addressed to them
- Receive delivery notifications

## Package Status Flow

Created → Assigned → Picked Up → In Transit → Delivered ↓ Failed


## WebSocket Events

### Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/connect?token=<jwt_token>');
```

### Event Types

connection_established - Connection confirmed

package_created - New package created

package_status_updated - Package status changed

package_assigned_to_you - Package assigned to courier

system_announcement - System-wide notifications

### Error Handling

### HTTP Status Codes

200 - Success

201 - Created

400 - Bad Request

401 - Unauthorized

403 - Forbidden

404 - Not Found

422 - Validation Error

500 - Internal Server Error

### Error Response Format

```json
{
  "detail": "Error description"
}
```

### Validation Error Format

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Rate Limiting

Authentication endpoints: 5 requests per minute

General API: 100 requests per minute

WebSocket connections: 1 per user

### Pagination

List endpoints support pagination:

```
GET /api/packages/?skip=0&limit=10
```

skip: Number of records to skip (default: 0)

limit: Maximum records to return (default: 10, max: 100)


## Examples

### Register User

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "name": "John Doe",
    "password": "securepass123",
    "role": "sender",
    "phone": "+1234567890"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

### Create Package

```bash
curl -X POST "http://localhost:8000/api/packages/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Important Documents",
    "description": "Legal documents for delivery",
    "sender_name": "John Doe",
    "sender_phone": "+1234567890",
    "sender_address": "123 Main St, City, State",
    "recipient_name": "Jane Smith",
    "recipient_phone": "+1234567891",
    "recipient_address": "456 Oak Ave, City, State"
  }'
```

### Update Package Status

```bash
curl -X PUT "http://localhost:8000/api/packages/1/status" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "picked_up"
  }'
```


## SDKs and Libraries

### JavaScript/TypeScript

```javascript
// Example API client
class CourierAPI {
  constructor(baseURL, token) {
    this.baseURL = baseURL;
    this.token = token;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${this.token}`,
        ...options.headers
      },
      ...options
    };

    const response = await fetch(url, config);
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    
    return response.json();
  }

  // Auth methods
  async login(email, password) {
    return this.request('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
  }

  // Package methods
  async getPackages(skip = 0, limit = 10) {
    return this.request(`/api/packages/?skip=${skip}&limit=${limit}`);
  }

  async createPackage(packageData) {
    return this.request('/api/packages/', {
      method: 'POST',
      body: JSON.stringify(packageData)
    });
  }
}
```

### Python

```python
import requests

class CourierAPI:
    def __init__(self, base_url, token=None):
        self.base_url = base_url
        self.token = token
        self.session = requests.Session()
        
        if token:
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
    
    def login(self, email, password):
        response = self.session.post(
            f'{self.base_url}/api/auth/login',
            json={'email': email, 'password': password}
        )
        response.raise_for_status()
        data = response.json()
        self.token = data['access_token']
        self.session.headers.update({
            'Authorization': f'Bearer {self.token}'
        })
        return data
    
    def get_packages(self, skip=0, limit=10):
        response = self.session.get(
            f'{self.base_url}/api/packages/',
            params={'skip': skip, 'limit': limit}
        )
        response.raise_for_status()
        return response.json()
    
    def create_package(self, package_data):
        response = self.session.post(
            f'{self.base_url}/api/packages/',
            json=package_data
        )
        response.raise_for_status()
        return response.json()
```

